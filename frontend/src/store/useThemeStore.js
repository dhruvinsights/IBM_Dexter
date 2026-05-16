import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const CARBON_THEMES = {
  DARK: 'g100',
  LIGHT: 'white',
};

const useThemeStore = create(
  persist(
    (set) => ({
      theme: CARBON_THEMES.DARK,
      setTheme: (theme) => set({ theme }),
      toggleTheme: () =>
        set((state) => ({
          theme:
            state.theme === CARBON_THEMES.LIGHT
              ? CARBON_THEMES.DARK
              : CARBON_THEMES.LIGHT,
        })),
    }),
    {
      name: 'dexter-theme',
    }
  )
);

export default useThemeStore;

// Made with Bob
