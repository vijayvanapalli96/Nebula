export interface Question {
  id: string;
  question: string;
  options: string[];
}

export interface StoryQuestionsResponse {
  questions: Question[];
}

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

  // API response has no `id` — generate stable ids from index
  return {
    questions: data.questions.map((q, i) => ({
      id: `q_${i}`,
      question: q.question,
      options: q.options,
    })),
  };
}
