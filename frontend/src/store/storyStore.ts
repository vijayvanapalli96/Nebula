import { create } from 'zustand';
import type { Genre, NewStoryForm, Story } from '../types/story';

// ─── Mock Data ────────────────────────────────────────────────────────────────

const MOCK_STORIES: Story[] = [
  {
    id: 'story-1',
    title: 'The Last Case of Detective Hale',
    genre: 'Noir Detective',
    progress: 60,
    coverImage:
      'https://images.unsplash.com/photo-1605806616949-1e87b487fc2f?w=600&q=80',
    lastPlayed: '2026-03-12T21:30:00Z',
  },
  {
    id: 'story-2',
    title: 'Beyond the Andromeda Gate',
    genre: 'Sci-Fi Exploration',
    progress: 25,
    coverImage:
      'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=600&q=80',
    lastPlayed: '2026-03-10T15:00:00Z',
  },
  {
    id: 'story-3',
    title: 'Mirrors of the Mind',
    genre: 'Psychological Thriller',
    progress: 82,
    coverImage:
      'https://images.unsplash.com/photo-1518895312237-a9e23508077d?w=600&q=80',
    lastPlayed: '2026-03-13T09:15:00Z',
  },
  {
    id: 'story-4',
    title: 'The Iron Throne of Elaryn',
    genre: 'Fantasy Kingdom',
    progress: 10,
    coverImage:
      'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&q=80',
    lastPlayed: '2026-03-08T18:45:00Z',
  },
  {
    id: 'story-5',
    title: 'Ash & Ember',
    genre: 'Post-Apocalyptic',
    progress: 47,
    coverImage:
      'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
    lastPlayed: '2026-03-11T12:00:00Z',
  },
];

// ─── Store Types ──────────────────────────────────────────────────────────────

interface StoryState {
  stories: Story[];
  genres: Genre[];
  selectedGenre: Genre | null;
  activeStory: Story | null;
  isModalOpen: boolean;
  newStoryForm: NewStoryForm;

  // Actions
  setSelectedGenre: (genre: Genre | null) => void;
  setActiveStory: (story: Story | null) => void;
  openModal: (genre: Genre) => void;
  closeModal: () => void;
  updateForm: (fields: Partial<NewStoryForm>) => void;
  resetForm: () => void;
  setGenres: (genres: Genre[]) => void;
}

const defaultForm: NewStoryForm = {
  characterName: '',
  archetype: '',
  motivation: '',
};

// ─── Store ────────────────────────────────────────────────────────────────────

export const useStoryStore = create<StoryState>((set) => ({
  stories: MOCK_STORIES,
  genres: [],
  selectedGenre: null,
  activeStory: null,
  isModalOpen: false,
  newStoryForm: defaultForm,

  setSelectedGenre: (genre) => set({ selectedGenre: genre }),
  setActiveStory: (story) => set({ activeStory: story }),

  openModal: (genre) =>
    set({ selectedGenre: genre, isModalOpen: true, newStoryForm: defaultForm }),

  closeModal: () =>
    set({ isModalOpen: false, selectedGenre: null }),

  updateForm: (fields) =>
    set((state) => ({ newStoryForm: { ...state.newStoryForm, ...fields } })),

  resetForm: () => set({ newStoryForm: defaultForm }),
  setGenres: (genres) => set({ genres }),
}));
