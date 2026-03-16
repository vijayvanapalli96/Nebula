import { create } from 'zustand';
import { loadThemes } from '../services/themeService';
import type { Genre } from '../types/story';

/** Deterministic-ish shuffle — no external deps required */
function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

interface StoryThemeState {
  themes: Genre[];
  featuredThemes: Genre[]; // 4 random picks
  loading: boolean;
  error: string | null;

  /** Fetches themes once; subsequent calls are no-ops (cached). */
  fetchThemes: () => Promise<void>;
  setThemes: (themes: Genre[]) => void;
  setFeaturedThemes: (themes: Genre[]) => void;
}

export const useStoryThemeStore = create<StoryThemeState>((set, get) => ({
  themes: [],
  featuredThemes: [],
  loading: false,
  error: null,

  fetchThemes: async () => {
    // Cache — skip network if already populated
    if (get().themes.length > 0) return;

    set({ loading: true, error: null });
    try {
      const themes = await loadThemes();
      const featured = shuffle(themes).slice(0, 4);
      set({ themes, featuredThemes: featured, loading: false });
    } catch (err) {
      set({
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to load themes from the server.',
      });
      // Re-throw so callers (ThemeLoadingPage) know the fetch failed
      throw err;
    }
  },

  setThemes: (themes) => {
    const featured = shuffle(themes).slice(0, 4);
    set({ themes, featuredThemes: featured });
  },

  setFeaturedThemes: (featuredThemes) => set({ featuredThemes }),
}));
