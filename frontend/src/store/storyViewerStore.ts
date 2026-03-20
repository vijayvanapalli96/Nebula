import { create } from 'zustand';
import { fetchStoryDetail, fetchContinuationScene, fetchSceneMedia, fetchStoryOpening } from '../api/storyApi';
import type { ChoiceMediaItem } from '../api/storyApi';
import type { SceneDoc, StoryDetail } from '../types/story';
import { gcsPathToUrl } from '../utils/gcs';
import type { Question } from './storyCreationStore';

// ── Scene timeline builder ────────────────────────────────────────────────────

/**
 * Traverse the scene tree from rootSceneId, following selected-choice links
 * (choices where nextSceneId != null).
 * Returns ordered scenes representing the user's current story path.
 */
export function buildSceneTimeline(rootSceneId: string, scenes: SceneDoc[]): SceneDoc[] {
  const map = new Map(scenes.map((s) => [s.sceneId, s]));
  const timeline: SceneDoc[] = [];
  const visited = new Set<string>(); // guard against cycles

  let current = map.get(rootSceneId);
  while (current && !visited.has(current.sceneId)) {
    timeline.push(current);
    visited.add(current.sceneId);
    const selected = current.choices.find((c) => c.nextSceneId != null);
    if (!selected?.nextSceneId) break;
    current = map.get(selected.nextSceneId);
  }

  return timeline;
}

// ── Store ─────────────────────────────────────────────────────────────────────

interface StoryViewerState {
  story: StoryDetail | null;
  scenes: SceneDoc[];
  /** Ordered scenes from root → current unresolved scene. */
  timeline: SceneDoc[];
  /** sceneId → choiceId that was selected (recovered from Firestore data). */
  selectedChoices: Record<string, string>;
  /** sceneId → true once the user has clicked "Make Your Choice". */
  choicesRevealedForScene: Record<string, boolean>;
  /** sceneId → choiceId selected this session (not yet confirmed by API). */
  localSelectedChoice: Record<string, string>;
  /** True while waiting for next-scene generation after a local choice. */
  generatingNextScene: boolean;
  /** sceneId → true while polling GET /story/media for images. */
  mediaLoadingForScene: Record<string, boolean>;
  /** sceneId → true once all choice images have been received. */
  mediaReadyForScene: Record<string, boolean>;
  loading: boolean;
  error: string | null;
  /** Current lifecycle phase of the story. */
  phase: 'loading' | 'questions' | 'generating' | 'playing' | 'error';
  /** Questions fetched from Firestore for this story. */
  storyQuestions: Question[];
  /** User's answers: questionId → selected label. */
  questionAnswers: Record<string, string>;
  /** Optional custom input / character name. */
  questionCustomInput: string;
  /** True while POST /story/opening is in-flight. */
  generatingScene: boolean;

  /** Load story from API (or use prefetched data from navigation state). */
  loadStory: (storyId: string, prefetched?: StoryDetail | null, silent?: boolean) => Promise<void>;
  /** Mark a choice selection recovered from Firestore data. */
  selectChoice: (sceneId: string, choiceId: string) => void;
  /** Reveal the choice grid for a leaf scene after the unlock button is clicked. */
  revealChoices: (sceneId: string) => void;
  /** Set a locally chosen option, call the API, and append the new scene. */
  selectLocalChoice: (sceneId: string, choiceId: string) => Promise<void>;
  /** Append a newly generated scene to the timeline and mark generation complete. */
  appendScene: (scene: SceneDoc) => void;
  /** Begin polling GET /story/media until all choice images are ready, then reveal choices. */
  startMediaPolling: (sceneId: string) => void;
  /** Merge polled imageUrl/videoUrl into timeline choices and mark scene media ready. */
  mergeChoiceMedia: (sceneId: string, items: ChoiceMediaItem[]) => void;
  /** Store an answer to a story question. */
  setQuestionAnswer: (questionId: string, label: string) => void;
  /** Update the custom story input / character name. */
  setQuestionCustomInput: (value: string) => void;
  /** Submit questionnaire answers and trigger opening scene generation. */
  submitQuestionnaire: () => Promise<void>;
  reset: () => void;
}

export const useStoryViewerStore = create<StoryViewerState>((set, get) => ({
  story: null,
  scenes: [],
  timeline: [],
  selectedChoices: {},
  choicesRevealedForScene: {},
  localSelectedChoice: {},
  generatingNextScene: false,
  mediaLoadingForScene: {},
  mediaReadyForScene: {},
  loading: false,
  error: null,
  phase: 'loading',
  storyQuestions: [],
  questionAnswers: {},
  questionCustomInput: '',
  generatingScene: false,

  loadStory: async (storyId, prefetched, silent = false) => {
    if (!silent) set({ loading: true, error: null, phase: 'loading' });
    try {
      const story = prefetched ?? (await fetchStoryDetail(storyId));

      // Normalize GCS paths → https:// URLs across all subcollections
      const scenes = ((story.scenes ?? []) as SceneDoc[]).map((scene) => ({
        ...scene,
        choices: scene.choices.map((c) => ({
          ...c,
          imageUrl: gcsPathToUrl(c.imageUrl) ?? null,
          videoUrl: gcsPathToUrl(c.videoUrl) ?? null,
        })),
      }));

      const questions = (story.questions ?? []).map((q) => ({
        ...q,
        options: ((q.options as Record<string, unknown>[]) ?? []).map((opt) => ({
          ...opt,
          imageUrl: gcsPathToUrl(opt.imageUrl as string | null) ?? null,
        })),
      }));

      const answers = (story.answers ?? []).map((a) => ({
        ...a,
        imageUrl: gcsPathToUrl(a.imageUrl as string | null) ?? null,
      }));

      const normalizedStory = { ...story, questions, answers };

      // Determine root scene
      const rootId =
        story.root_scene_id ??
        scenes.find((s) => s.isRoot)?.sceneId ??
        scenes[0]?.sceneId;

      const timeline = rootId ? buildSceneTimeline(rootId, scenes) : [];

      // Recover already-made selections from Firestore data
      const selectedChoices: Record<string, string> = {};
      for (const scene of timeline) {
        const sel = scene.choices.find((c) => c.nextSceneId != null);
        if (sel) selectedChoices[scene.sceneId] = sel.choiceId;
      }

      // Determine lifecycle phase
      const hasScenes = scenes.length > 0;
      const questionnaireCompleted = story.questionnaire_completed ?? false;
      let storyPhase: 'playing' | 'questions' | 'generating' = 'playing';
      if (!hasScenes) {
        storyPhase = questionnaireCompleted ? 'generating' : 'questions';
      }

      // Map Firestore questions into typed Question[]
      const storyQuestions: Question[] = (normalizedStory.questions ?? []).map((q, idx) => {
        const qr = q as Record<string, unknown>;
        return {
          id: String(qr.questionId ?? qr.question_id ?? `q_${idx}`),
          question: String(qr.question ?? ''),
          options: ((qr.options ?? []) as Record<string, unknown>[]).map((opt, oi) => ({
            label: String(opt.label ?? opt.text ?? `Option ${oi + 1}`),
            image: String(opt.imageUrl ?? opt.image ?? ''),
          })),
        };
      });

      // Recover any already-submitted answers
      const questionAnswers: Record<string, string> = {};
      for (const ans of (normalizedStory.answers ?? [])) {
        const a = ans as Record<string, unknown>;
        const qId = String(a.questionId ?? a.question_id ?? '');
        const selected = String(a.selectedOption ?? a.selected_option ?? '');
        if (qId && selected) questionAnswers[qId] = selected;
      }

      set({
        story: normalizedStory, scenes, timeline, selectedChoices,
        loading: false, phase: storyPhase, storyQuestions, questionAnswers,
      });

      // Auto-retrigger generation if answers were submitted but scene never stored
      if (storyPhase === 'generating') {
        void get().submitQuestionnaire();
      }
    } catch (err) {
      set({
        loading: false,
        phase: 'error',
        error: err instanceof Error ? err.message : 'Failed to load story.',
      });
    }
  },

  selectChoice: (sceneId, choiceId) =>
    set((state) => ({
      selectedChoices: { ...state.selectedChoices, [sceneId]: choiceId },
    })),

  revealChoices: (sceneId) =>
    set((state) => ({
      choicesRevealedForScene: { ...state.choicesRevealedForScene, [sceneId]: true },
    })),

  appendScene: (newScene) =>
    set((state) => {
      // Promote the locally-selected choice to the confirmed selectedChoices map
      // so the timeline connector appears between the two scenes.
      const parentSceneId = newScene.parentSceneId ?? '';
      const choiceId = state.localSelectedChoice[parentSceneId] ?? '';
      return {
        timeline: [...state.timeline, newScene],
        scenes: [...state.scenes, newScene],
        generatingNextScene: false,
        selectedChoices: choiceId
          ? { ...state.selectedChoices, [parentSceneId]: choiceId }
          : state.selectedChoices,
      };
    }),

  mergeChoiceMedia: (sceneId, items) =>
    set((state) => {
      const itemMap = new Map(items.map((i) => [i.choice_id, i]));
      const mergeIntoScene = (s: SceneDoc) => {
        if (s.sceneId !== sceneId) return s;
        return {
          ...s,
          choices: s.choices.map((c) => {
            const media = itemMap.get(c.choiceId);
            if (!media) return c;
            return {
              ...c,
              imageUrl: gcsPathToUrl(media.image_url) ?? c.imageUrl,
              videoUrl: gcsPathToUrl(media.video_url) ?? c.videoUrl,
            };
          }),
        };
      };
      return {
        timeline: state.timeline.map(mergeIntoScene),
        scenes: state.scenes.map(mergeIntoScene),
        mediaLoadingForScene: { ...state.mediaLoadingForScene, [sceneId]: false },
        mediaReadyForScene: { ...state.mediaReadyForScene, [sceneId]: true },
        // Auto-reveal choices now that images are ready
        choicesRevealedForScene: { ...state.choicesRevealedForScene, [sceneId]: true },
      };
    }),

  startMediaPolling: (sceneId) => {
    const { story } = get();
    if (!story) return;

    set((state) => ({
      mediaLoadingForScene: { ...state.mediaLoadingForScene, [sceneId]: true },
    }));

    const MAX_ATTEMPTS = 20; // 20 × 3 s = 60 s max
    const INTERVAL_MS = 3000;
    let attempts = 0;
    const storyId = story.story_id;

    const tick = async () => {
      // Abort if the user navigated away or images already arrived via another path
      if (!get().story || get().mediaReadyForScene[sceneId]) return;

      attempts++;
      try {
        const items = await fetchSceneMedia(storyId, sceneId);
        const expectedCount =
          get().timeline.find((s) => s.sceneId === sceneId)?.choices.length ?? 0;
        const allReady =
          expectedCount > 0 &&
          items.length >= expectedCount &&
          items.every((c) => c.image_url !== null);

        if (allReady || attempts >= MAX_ATTEMPTS) {
          get().mergeChoiceMedia(sceneId, items);
        } else {
          setTimeout(tick, INTERVAL_MS);
        }
      } catch {
        if (attempts >= MAX_ATTEMPTS) {
          get().mergeChoiceMedia(sceneId, []);
        } else {
          setTimeout(tick, INTERVAL_MS);
        }
      }
    };

    setTimeout(tick, INTERVAL_MS);
  },

  selectLocalChoice: async (sceneId, choiceId) => {
    // Immediately highlight the selected choice and show the generating banner.
    set((state) => ({
      localSelectedChoice: { ...state.localSelectedChoice, [sceneId]: choiceId },
      generatingNextScene: true,
      error: null,
    }));

    const { story, scenes, appendScene } = get();
    if (!story) return;

    const currentScene = scenes.find((s) => s.sceneId === sceneId);
    // Fall back to sceneId itself — backend ignores this field but schema requires min_length=1
    const parentSceneId = currentScene?.parentSceneId || sceneId;

    try {
      const response = await fetchContinuationScene({
        story_id: story.story_id,
        current_scene_id: sceneId,
        choice_id: choiceId,
        previous_scene_id: parentSceneId,
      });

      const newScene: SceneDoc = {
        sceneId: response.scene_id,
        title: response.scene_title,
        description: response.scene_description,
        isRoot: false,
        parentSceneId: response.parent_scene_id,
        depth: response.depth,
        nextSceneIds: [],
        createdAt: new Date().toISOString(),
        choices: response.choices.map((c) => ({
          choiceId: c.choice_id,
          choiceText: c.choice_text,
          directionHint: c.direction_hint,
          imagePrompt: c.image_prompt,
          videoPrompt: c.video_prompt,
          nextSceneId: null,
          imageUrl: null,
          videoUrl: null,
        })),
      };

      appendScene(newScene);
    } catch (err) {
      set({
        generatingNextScene: false,
        error: err instanceof Error ? err.message : 'Failed to generate next scene.',
      });
    }
  },

  setQuestionAnswer: (questionId, label) =>
    set((state) => ({
      questionAnswers: { ...state.questionAnswers, [questionId]: label },
    })),

  setQuestionCustomInput: (value) => set({ questionCustomInput: value }),

  submitQuestionnaire: async () => {
    const { story, storyQuestions, questionAnswers, questionCustomInput } = get();
    if (!story) return;

    set({ phase: 'generating', generatingScene: true, error: null });

    const answersPayload = storyQuestions.map((q) => {
      const selectedLabel = questionAnswers[q.id] ?? '';
      const matchedOption = q.options.find((o) => o.label === selectedLabel);
      return {
        question_id: q.id,
        question: q.question,
        selected_option: selectedLabel,
        image_url: matchedOption?.image ?? '',
      };
    });

    try {
      await fetchStoryOpening({
        story_id: story.story_id,
        theme_id: story.theme_id ?? '',
        character_name: questionCustomInput.trim() || 'The Protagonist',
        answers: answersPayload,
        custom_input: questionCustomInput.trim(),
      });
      set({ generatingScene: false });
      // Silently reload from Firestore — loadStory will set phase='playing'
      await get().loadStory(story.story_id, null, true);
    } catch (err) {
      set({
        generatingScene: false,
        phase: 'questions',
        error: err instanceof Error ? err.message : 'Failed to generate story. Please try again.',
      });
    }
  },

  reset: () =>
    set({
      story: null,
      scenes: [],
      timeline: [],
      selectedChoices: {},
      choicesRevealedForScene: {},
      localSelectedChoice: {},
      generatingNextScene: false,
      mediaLoadingForScene: {},
      mediaReadyForScene: {},
      loading: false,
      error: null,
      phase: 'loading',
      storyQuestions: [],
      questionAnswers: {},
      questionCustomInput: '',
      generatingScene: false,
    }),
}));
