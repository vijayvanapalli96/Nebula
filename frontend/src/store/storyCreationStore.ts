import { create } from 'zustand';
import type { Genre } from '../types/story';

export interface QuestionOption {
  label: string;
  image: string;
}

export interface Question {
  id: string;
  question: string;
  options: QuestionOption[];
}

// Total steps = questions + 1 custom-input screen
// currentQuestionIndex === questions.length  →  custom input screen
interface StoryCreationState {
  questions: Question[];
  answers: Record<string, string>;
  customInput: string;
  loading: boolean;
  selectedGenre: Genre | null;
  currentQuestionIndex: number;

  setQuestions: (questions: Question[]) => void;
  setAnswer: (questionId: string, option: string) => void;
  setCustomInput: (value: string) => void;
  setLoading: (loading: boolean) => void;
  setSelectedGenre: (genre: Genre | null) => void;
  updateOptionImage: (questionIndex: number, optionIndex: number, imageUrl: string) => void;
  nextQuestion: () => void;
  previousQuestion: () => void;
  goToQuestion: (index: number) => void;
  reset: () => void;
}

export const useStoryCreationStore = create<StoryCreationState>((set, get) => ({
  questions: [],
  answers: {},
  customInput: '',
  loading: false,
  selectedGenre: null,
  currentQuestionIndex: 0,

  setQuestions: (questions) => set({ questions }),
  setAnswer: (questionId, option) =>
    set((state) => ({ answers: { ...state.answers, [questionId]: option } })),
  setCustomInput: (customInput) => set({ customInput }),
  setLoading: (loading) => set({ loading }),
  setSelectedGenre: (selectedGenre) => set({ selectedGenre }),
  updateOptionImage: (questionIndex, optionIndex, imageUrl) =>
    set((state) => {
      const questions = state.questions.map((q, qi) => {
        if (qi !== questionIndex) return q;
        return {
          ...q,
          options: q.options.map((opt, oi) =>
            oi === optionIndex ? { ...opt, image: imageUrl } : opt,
          ),
        };
      });
      return { questions };
    }),
  nextQuestion: () => {
    const { currentQuestionIndex, questions } = get();
    // Allow advancing to custom-input screen (index === questions.length)
    if (currentQuestionIndex <= questions.length - 1) {
      set({ currentQuestionIndex: currentQuestionIndex + 1 });
    }
  },
  previousQuestion: () => {
    const { currentQuestionIndex } = get();
    if (currentQuestionIndex > 0) {
      set({ currentQuestionIndex: currentQuestionIndex - 1 });
    }
  },
  goToQuestion: (index) => set({ currentQuestionIndex: index }),
  reset: () =>
    set({
      questions: [],
      answers: {},
      customInput: '',
      loading: false,
      selectedGenre: null,
      currentQuestionIndex: 0,
    }),
}));
