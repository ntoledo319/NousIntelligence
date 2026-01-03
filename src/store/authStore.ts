import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  name: string;
  email?: string;
  isDemo: boolean;
  preferences?: {
    theme: string;
    locale: string;
    notifications: boolean;
  };
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User) => void;
  logout: () => void;
  updatePreferences: (preferences: Partial<User['preferences']>) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,

      login: (user) =>
        set({
          user,
          isAuthenticated: true,
          isLoading: false,
        }),

      logout: () => {
        set({
          user: null,
          isAuthenticated: false,
        });
        window.location.href = '/';
      },

      updatePreferences: (preferences) =>
        set((state) => ({
          user: state.user
            ? {
                ...state.user,
                preferences: { ...state.user.preferences, ...preferences },
              }
            : null,
        })),

      checkAuth: async () => {
        try {
          const response = await fetch('/api/user');
          if (response.ok) {
            const data = await response.json();
            if (data.user && data.user.id !== 'guest') {
              set({
                user: {
                  id: data.user.id,
                  name: data.user.name,
                  email: data.user.email,
                  isDemo: data.user.id === 'demo',
                  preferences: data.user.preferences,
                },
                isAuthenticated: true,
                isLoading: false,
              });
            } else {
              set({ isLoading: false });
            }
          } else {
            set({ isLoading: false });
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'nous-auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
