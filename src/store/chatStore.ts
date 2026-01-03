import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  emotion?: string;
  skillRecommendations?: string[];
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentEmotion: string | null;
  conversationId: string | null;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  setEmotion: (emotion: string) => void;
  clearChat: () => void;
  loadHistory: (conversationId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      isLoading: false,
      currentEmotion: null,
      conversationId: null,

      addMessage: (message) => {
        const newMessage: Message = {
          ...message,
          id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
        };
        set((state) => ({
          messages: [...state.messages, newMessage],
        }));
      },

      setLoading: (loading) => set({ isLoading: loading }),

      setEmotion: (emotion) => set({ currentEmotion: emotion }),

      clearChat: () =>
        set({
          messages: [],
          currentEmotion: null,
          conversationId: null,
        }),

      loadHistory: async (conversationId) => {
        try {
          const response = await fetch(`/api/v1/conversations/${conversationId}/messages`);
          if (response.ok) {
            const data = await response.json();
            set({
              messages: data.messages || [],
              conversationId,
            });
          }
        } catch (error) {
          console.error('Failed to load chat history:', error);
        }
      },
    }),
    {
      name: 'nous-chat-storage',
      partialize: (state) => ({
        messages: state.messages.slice(-50),
        conversationId: state.conversationId,
      }),
    }
  )
);
