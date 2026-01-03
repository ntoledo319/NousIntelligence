import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface DBTSkill {
  id: string;
  name: string;
  category: string;
  description: string;
  effectiveness?: number;
}

export interface MoodEntry {
  id: string;
  mood: number;
  note: string;
  timestamp: Date;
  activities?: string[];
}

export interface ThoughtRecord {
  id: string;
  situation: string;
  automaticThought: string;
  emotion: string;
  evidence: string[];
  alternativeThought: string;
  outcome: string;
  timestamp: Date;
}

export interface TherapeuticState {
  dbtSkills: DBTSkill[];
  moodHistory: MoodEntry[];
  thoughtRecords: ThoughtRecord[];
  isLoading: boolean;
  addMoodEntry: (mood: Omit<MoodEntry, 'id' | 'timestamp'>) => Promise<void>;
  addThoughtRecord: (thought: Omit<ThoughtRecord, 'id' | 'timestamp'>) => Promise<void>;
  logDBTSkill: (skill: Omit<DBTSkill, 'id'>) => Promise<void>;
  loadData: () => Promise<void>;
}

export const useTherapeuticStore = create<TherapeuticState>()(
  persist(
    (set, get) => ({
      dbtSkills: [],
      moodHistory: [],
      thoughtRecords: [],
      isLoading: false,

      addMoodEntry: async (moodData) => {
        set({ isLoading: true });
        try {
          const response = await fetch('/api/v1/therapeutic/mood', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(moodData),
          });

          if (response.ok) {
            const data = await response.json();
            const newEntry: MoodEntry = {
              ...moodData,
              id: data.id,
              timestamp: new Date(data.timestamp),
            };
            set((state) => ({
              moodHistory: [...state.moodHistory, newEntry],
            }));
          }
        } catch (error) {
          console.error('Failed to add mood entry:', error);
        } finally {
          set({ isLoading: false });
        }
      },

      addThoughtRecord: async (thoughtData) => {
        set({ isLoading: true });
        try {
          const response = await fetch('/api/v1/therapeutic/cbt/thoughts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(thoughtData),
          });

          if (response.ok) {
            const data = await response.json();
            const newRecord: ThoughtRecord = {
              ...thoughtData,
              id: data.id,
              timestamp: new Date(),
            };
            set((state) => ({
              thoughtRecords: [...state.thoughtRecords, newRecord],
            }));
          }
        } catch (error) {
          console.error('Failed to add thought record:', error);
        } finally {
          set({ isLoading: false });
        }
      },

      logDBTSkill: async (skillData) => {
        set({ isLoading: true });
        try {
          const response = await fetch('/api/v1/therapeutic/dbt/skills/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(skillData),
          });

          if (response.ok) {
            const data = await response.json();
            set((state) => ({
              dbtSkills: [...state.dbtSkills, { ...skillData, id: data.id }],
            }));
          }
        } catch (error) {
          console.error('Failed to log DBT skill:', error);
        } finally {
          set({ isLoading: false });
        }
      },

      loadData: async () => {
        set({ isLoading: true });
        try {
          const [moodRes, thoughtsRes, skillsRes] = await Promise.all([
            fetch('/api/v1/therapeutic/mood'),
            fetch('/api/v1/therapeutic/cbt/thoughts'),
            fetch('/api/v1/therapeutic/dbt/skills/logs'),
          ]);

          const [moods, thoughts, skills] = await Promise.all([
            moodRes.ok ? moodRes.json() : [],
            thoughtsRes.ok ? thoughtsRes.json() : [],
            skillsRes.ok ? skillsRes.json() : [],
          ]);

          set({
            moodHistory: moods,
            thoughtRecords: thoughts,
            dbtSkills: skills,
          });
        } catch (error) {
          console.error('Failed to load therapeutic data:', error);
        } finally {
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'nous-therapeutic-storage',
      partialize: (state) => ({
        moodHistory: state.moodHistory.slice(-100),
        thoughtRecords: state.thoughtRecords.slice(-50),
      }),
    }
  )
);
