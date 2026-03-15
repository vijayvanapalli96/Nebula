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

export const FALLBACK_GENRES: Genre[] = [
  {
    id: 'genre-noir',
    title: 'Noir Detective',
    tagline: 'Solve a crime in a rain-soaked city.',
    description: 'Secrets hide in every shadow.\nCan you uncover the truth?',
    image:
      'https://images.unsplash.com/photo-1605806616949-1e87b487fc2f?w=800&q=80',
    accentColor: 'rgba(234,179,8,0.6)',
  },
  {
    id: 'genre-scifi',
    title: 'Sci-Fi Exploration',
    tagline: 'Discover secrets beyond the stars.',
    description: 'The cosmos holds answers.\nDare to ask the questions.',
    image:
      'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&q=80',
    accentColor: 'rgba(59,130,246,0.6)',
  },
  {
    id: 'genre-thriller',
    title: 'Psychological Thriller',
    tagline: 'Reality may not be what it seems.',
    description: 'Your mind is both prison and key.\nTrust nothing.',
    image:
      'https://images.unsplash.com/photo-1518895312237-a9e23508077d?w=800&q=80',
    accentColor: 'rgba(239,68,68,0.6)',
  },
  {
    id: 'genre-fantasy',
    title: 'Fantasy Kingdom',
    tagline: 'Magic, politics, and ancient power.',
    description: 'A throne of lies. A destiny of fire.\nRise or be forgotten.',
    image:
      'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80',
    accentColor: 'rgba(168,85,247,0.6)',
  },
  {
    id: 'genre-apocalyptic',
    title: 'Post-Apocalyptic',
    tagline: 'Survive a ruined world.',
    description: 'The old world is ash.\nYour choices write the new one.',
    image:
      'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    accentColor: 'rgba(249,115,22,0.6)',
  },
  {
    id: 'genre-political',
    title: 'Political Conspiracy',
    tagline: 'Truth is buried beneath power.',
    description: 'Everyone has an agenda.\nOnly you can expose it.',
    image:
      'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80',
    accentColor: 'rgba(20,184,166,0.6)',
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
  genres: FALLBACK_GENRES,
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
