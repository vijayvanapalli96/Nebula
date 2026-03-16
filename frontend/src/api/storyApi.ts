import { auth } from '../lib/firebase';
import type { Question, QuestionOption } from '../store/storyCreationStore';
import type { Genre } from '../types/story';
import type { Scene } from '../store/storySessionStore';

export interface StoryQuestionsResponse {
  questions: Question[];
  storyId: string | null;
}

type QuestionOptionPayload = string | { text: string; image_prompt?: string; image_uri?: string | null };

interface QuestionPayload {
  question_id?: string;
  question: string;
  options: QuestionOptionPayload[];
}

interface StoryQuestionsPayload {
  story_id?: string | null;
  theme: string;
  questions: QuestionPayload[];
}

interface StoryThemePayload {
  id: string;
  title: string;
  tagline: string;
  description: string;
  image: string;
  accent_color: string;
}

export interface StoryScenePayload {
  scene_id: string;
  story_id: string;
  chapter_number: number;
  scene_number: number;
  title: string;
  description: string;
  short_summary: string;
  full_narrative: string;
  parent_scene_id: string | null;
  selected_choice_id_from_parent: string | null;
  path_depth: number;
  is_root: boolean;
  is_current_checkpoint: boolean;
  is_ending: boolean;
  ending_type: string | null;
  scene_type: string;
  mood: string;
  location: { name: string; type: string } | null;
  characters_present: string[];
  asset_refs: {
    hero_image_id: string | null;
    scene_image_id: string | null;
    scene_video_id: string | null;
    scene_audio_id: string | null;
  };
  generation_status: {
    text: string;
    image: string;
    video: string;
  };
  created_at: string;
  updated_at: string;
}

const OPTION_IMAGES = [
  'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&q=80',
  'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
  'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=600&q=80',
  'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=600&q=80',
];

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

function mapQuestionOption(option: QuestionOptionPayload, index: number): QuestionOption {
  if (typeof option === 'string') {
    return {
      label: option,
      image: OPTION_IMAGES[index % OPTION_IMAGES.length],
    };
  }

  return {
    label: option.text,
    image: option.image_uri ?? OPTION_IMAGES[index % OPTION_IMAGES.length],
  };
}

export async function fetchStoryThemes(): Promise<Genre[]> {
  const res = await fetch(`${BASE_URL}/story/themes`);
  if (!res.ok) {
    throw new Error(`Failed to fetch story themes: ${res.status} ${res.statusText}`);
  }

  const payload = (await res.json()) as StoryThemePayload[];
  return payload.map((item) => ({
    id: item.id,
    title: item.title,
    tagline: item.tagline,
    description: item.description,
    image: item.image,
    accentColor: item.accent_color,
  }));
}

/** GET /stories/{storyId}/scenes — fetches saved scene graph nodes for a story. */
export async function fetchStoryScenes(storyId: string): Promise<StoryScenePayload[]> {
  const res = await fetch(`${BASE_URL}/stories/${storyId}/scenes`, {
    method: 'GET',
    headers: await getAuthHeaders(),
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch story scenes: ${res.status} ${res.statusText}`);
  }

  return (await res.json()) as StoryScenePayload[];
}

/**
 * Returns the current user's Firebase ID token, refreshing it if near expiry.
 * Throws if there is no signed-in user (should never happen inside ProtectedRoute).
 */
async function getAuthHeaders(): Promise<Record<string, string>> {
  const user = auth.currentUser;
  if (!user) throw new Error('No authenticated user.');
  const token = await user.getIdToken();
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

/** POST /story/questions — fetches AI-generated questions for the given theme/genre. */
export async function fetchStoryQuestions(themeId: string): Promise<StoryQuestionsResponse> {
  const res = await fetch(`${BASE_URL}/story/questions`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ theme_id: themeId }),
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch questions: ${res.status} ${res.statusText}`);
  }

  const data = (await res.json()) as StoryQuestionsPayload;

  // Diagnostic: log raw image_uri values so you can verify URLs in DevTools
  if (import.meta.env.DEV) {
    data.questions.forEach((q, qi) => {
      q.options.forEach((opt, oi) => {
        const raw = typeof opt === 'string' ? null : opt.image_uri;
        console.debug(`[storyApi] q${qi} opt${oi} image_uri =`, raw);
      });
    });
  }

  return {
    storyId: data.story_id ?? null,
    questions: data.questions.map((question, index) => ({
      id: question.question_id?.trim() ? question.question_id : `q_${index}`,
      question: question.question,
      options: question.options.map((option, optionIndex) => (
        mapQuestionOption(option, optionIndex)
      )),
    })),
  };
}

export interface StoryOpeningRequest {
  theme: string;
  character_name: string;
  answers: Array<{ question: string; answer: string }>;
}

/** POST /story/opening — generates the opening scene from the user's answers. */
export async function fetchStoryOpening(payload: StoryOpeningRequest): Promise<Scene> {
  const res = await fetch(`${BASE_URL}/story/opening`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Failed to generate story: ${res.status} ${res.statusText}`);
  }

  return res.json() as Promise<Scene>;
}
