import { create } from 'zustand';
import { fetchStoryDetail } from '../api/storyApi';
import type { SceneDoc, StoryDetail } from '../types/story';
import { gcsPathToUrl } from '../utils/gcs';

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
  loading: boolean;
  error: string | null;

  /** Load story from API (or use prefetched data from navigation state). */
  loadStory: (storyId: string, prefetched?: StoryDetail | null) => Promise<void>;
  /** Mark a choice selection recovered from Firestore data. */
  selectChoice: (sceneId: string, choiceId: string) => void;
  /** Reveal the choice grid for a leaf scene after the unlock button is clicked. */
  revealChoices: (sceneId: string) => void;
  /** Set a locally chosen option and begin the next-scene generation stub. */
  selectLocalChoice: (sceneId: string, choiceId: string) => void;
  reset: () => void;
}

export const useStoryViewerStore = create<StoryViewerState>((set) => ({
  story: null,
  scenes: [],
  timeline: [],
  selectedChoices: {},
  choicesRevealedForScene: {},
  localSelectedChoice: {},
  generatingNextScene: false,
  loading: false,
  error: null,

  loadStory: async (storyId, prefetched) => {
    set({ loading: true, error: null });
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

      set({ story: normalizedStory, scenes, timeline, selectedChoices, loading: false });
    } catch (err) {
      set({
        loading: false,
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

  selectLocalChoice: (sceneId, choiceId) => {
    // Stub — wire to POST /story/next-scene when backend endpoint is ready
    console.log('[Nebula] Next scene requested:', { sceneId, choiceId });
    set((state) => ({
      localSelectedChoice: { ...state.localSelectedChoice, [sceneId]: choiceId },
      generatingNextScene: true,
    }));
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
      loading: false,
      error: null,
    }),
}));
