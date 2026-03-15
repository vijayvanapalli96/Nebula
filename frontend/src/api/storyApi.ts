import type { Question, QuestionOption } from '../store/storyCreationStore';

export interface StoryQuestionsResponse {
  questions: Question[];
}

// Curated cinematic Unsplash images, cycled by option position (0-3)
const OPTION_IMAGES = [
  'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&q=80', // dark / moody
  'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80', // adventure / mountain
  'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=600&q=80', // thought / cosmos
  'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=600&q=80', // hopeful / sunrise
];

const BASE_URL = 'https://nebula-backend-979585801507.us-central1.run.app';

/** POST /story/questions — fetches AI-generated questions for the given theme/genre. */
export async function fetchStoryQuestions(theme: string): Promise<StoryQuestionsResponse> {
  const res = await fetch(`${BASE_URL}/story/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme }),
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch questions: ${res.status} ${res.statusText}`);
  }

  const data = await res.json() as {
    theme: string;
    questions: Array<{ question: string; options: string[] }>;
  };

  // API returns flat string options — map to { label, image }
  return {
    questions: data.questions.map((q, i) => ({
      id: `q_${i}`,
      question: q.question,
      options: q.options.map((label, oi): QuestionOption => ({
        label,
        image: OPTION_IMAGES[oi % OPTION_IMAGES.length],
      })),
    })),
  };
}
