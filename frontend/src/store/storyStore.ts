import { create } from 'zustand';
import { fetchUserStories } from '../api/storyApi';
import type { Genre, NewStoryForm, Story, UserStory } from '../types/story';

// ─── Store Types ──────────────────────────────────────────────────────────────

interface StoryState {
  // Legacy story list (kept for Story type compat)
  stories: Story[];
  // Real stories from API
  userStories: UserStory[];
  featuredUserStories: UserStory[]; // latest 4 for dashboard carousel
  storiesLoading: boolean;
  storiesError: string | null;

  genres: Genre[];
  selectedGenre: Genre | null;
  activeStory: Story | null;
  isModalOpen: boolean;
  newStoryForm: NewStoryForm;

  // Actions
  fetchUserStories: () => Promise<void>;
  setUserStories: (stories: UserStory[]) => void;
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

export const useStoryStore = create<StoryState>((set, get) => ({
  stories: [],
  userStories: [],
  featuredUserStories: [],
  storiesLoading: false,
  storiesError: null,

  genres: [],
  selectedGenre: null,
  activeStory: null,
  isModalOpen: false,
  newStoryForm: defaultForm,

  fetchUserStories: async () => {
    // Cache — skip if already populated
    if (get().userStories.length > 0) return;

    set({ storiesLoading: true, storiesError: null });
    try {
      const stories = await fetchUserStories();
      // Sort descending by updated_at so newest appears first
      const sorted = [...stories].sort(
        (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
      );
      const featured = sorted.slice(0, 4);
      set({ userStories: sorted, featuredUserStories: featured, storiesLoading: false });
    } catch (err) {
      set({
        storiesLoading: false,
        storiesError: err instanceof Error ? err.message : 'Failed to load stories.',
      });
    }
  },

  setUserStories: (stories) => {
    const sorted = [...stories].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
    );
    set({ userStories: sorted, featuredUserStories: sorted.slice(0, 4) });
  },

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
