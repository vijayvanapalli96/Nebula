import type { Question, QuestionOption } from '../store/storyCreationStore';
import type { Genre } from '../types/story';

export interface StoryQuestionsResponse {
  questions: Question[];
}

type QuestionOptionPayload = string | { text: string; image_uri?: string | null };

interface StoryQuestionsPayload {
  theme: string;
  questions: Array<{ question: string; options: QuestionOptionPayload[] }>;
}

interface StoryThemePayload {
  id: string;
  title: string;
  tagline: string;
  description: string;
  image: string;
  accent_color: string;
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

export async function fetchStoryQuestions(theme: string): Promise<StoryQuestionsResponse> {
  const res = await fetch(`${BASE_URL}/story/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme }),
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch questions: ${res.status} ${res.statusText}`);
  }

  const data = (await res.json()) as StoryQuestionsPayload;
  return {
    questions: data.questions.map((question, index) => ({
      id: `q_${index}`,
      question: question.question,
      options: question.options.map((option, optionIndex) => (
        mapQuestionOption(option, optionIndex)
      )),
    })),
  };
}
