import { create } from 'zustand';
import type { Genre } from '../types/story';

export interface Question {
  id: string;
  question: string;
  options: string[];
}

interface StoryCreationState {
  questions: Question[];
  answers: Record<string, string>;
  customInput: string;
  loading: boolean;
  selectedGenre: Genre | null;

  setQuestions: (questions: Question[]) => void;
  setAnswer: (questionId: string, option: string) => void;
  setCustomInput: (value: string) => void;
  setLoading: (loading: boolean) => void;
  setSelectedGenre: (genre: Genre | null) => void;
  reset: () => void;
}

export const useStoryCreationStore = create<StoryCreationState>((set) => ({
  questions: [],
  answers: {},
  customInput: '',
  loading: false,
  selectedGenre: null,

  setQuestions: (questions) => set({ questions }),
  setAnswer: (questionId, option) =>
    set((state) => ({ answers: { ...state.answers, [questionId]: option } })),
  setCustomInput: (customInput) => set({ customInput }),
  setLoading: (loading) => set({ loading }),
  setSelectedGenre: (selectedGenre) => set({ selectedGenre }),
  reset: () =>
    set({ questions: [], answers: {}, customInput: '', loading: false, selectedGenre: null }),
}));
