import { auth } from '../lib/firebase';
import type { Question, QuestionOption } from '../store/storyCreationStore';
import type { Scene } from '../store/storySessionStore';

export interface StoryQuestionsResponse {
  questions: Question[];
  mediaRequestId: string | null;
}

// Curated cinematic Unsplash images, cycled by option position (0-3)
const OPTION_IMAGES = [
  'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&q=80', // dark / moody
  'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80', // adventure / mountain
  'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=600&q=80', // thought / cosmos
  'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=600&q=80', // hopeful / sunrise
];

/**
 * Converts a GCS URI (gs://bucket/object) to a public HTTPS URL.
 * Returns the input unchanged if it is already an HTTP/HTTPS URL or empty.
 */
function gsToHttps(uri: string): string {
  if (!uri) return uri;
  if (uri.startsWith('gs://')) {
    // gs://bucket-name/path/to/file  →  https://storage.googleapis.com/bucket-name/path/to/file
    return uri.replace(/^gs:\/\//, 'https://storage.googleapis.com/');
  }
  return uri;
}

const BASE_URL = 'https://nebula-backend-979585801507.us-central1.run.app';

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
export async function fetchStoryQuestions(theme: string): Promise<StoryQuestionsResponse> {
  const res = await fetch(`${BASE_URL}/story/questions`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ theme }),
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch questions: ${res.status} ${res.statusText}`);
  }

  const data = await res.json() as {
    theme: string;
    questions: Array<{ question: string; options: Array<{ text: string; image_uri: string }> }>;
  };

  // API returns flat string options — map to { label, image }
  return {
    mediaRequestId: (data as { media_request_id?: string | null }).media_request_id ?? null,
    questions: data.questions.map((q, i) => ({
      id: `q_${i}`,
      question: q.question,
      options: q.options.map((opt, oi): QuestionOption => ({
        label: opt.text,
        image: opt.image_uri
          ? gsToHttps(opt.image_uri)
          : OPTION_IMAGES[oi % OPTION_IMAGES.length],
      })),
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

/** Map of asset_key → HTTPS URL (null = still generating, key absent = failed/missing). */
export type MediaAssets = Record<string, string | null>;

/** GET /story/media/{id} — returns current state of all generated image assets. */
export async function fetchMediaAssets(mediaRequestId: string): Promise<MediaAssets> {
  const res = await fetch(`${BASE_URL}/story/media/${mediaRequestId}`, {
    headers: await getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`Media poll failed: ${res.status}`);
  const data = await res.json() as { assets: Record<string, string | null> };
  // Convert any gs:// URIs to public HTTPS
  const converted: MediaAssets = {};
  for (const [key, uri] of Object.entries(data.assets)) {
    converted[key] = uri ? gsToHttps(uri) : null;
  }
  return converted;
}
