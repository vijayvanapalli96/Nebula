import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
  isDark: boolean;
  toggleTheme: () => void;
}

function applyTheme(isDark: boolean) {
  document.documentElement.classList.toggle('light', !isDark);
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      isDark: true,
      toggleTheme: () => {
        const next = !get().isDark;
        applyTheme(next);
        set({ isDark: next });
      },
    }),
    {
      name: 'nebula-theme',
      onRehydrateStorage: () => (state) => {
        applyTheme(state?.isDark ?? true);
      },
    },
  ),
);
