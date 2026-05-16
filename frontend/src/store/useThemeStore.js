import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useThemeStore = create(
  persist(
    (set) => ({
      theme: 'white',
      setTheme: (theme) => set({ theme }),
      toggleTheme: () =>
        set((state) => ({
          theme: state.theme === 'white' ? 'g100' : 'white',
        })),
    }),
    {
      name: 'dexter-theme',
    }
  )
);

export default useThemeStore;

// Made with Bob
