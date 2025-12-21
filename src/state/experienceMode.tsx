/**
 * Experience mode (Gentle vs Structured)
 *
 * Gentle:
 * - fewer panels, less density
 * Structured:
 * - more tools/insights visible by default
 *
 * @context_boundary UI preference only
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import { useLocalStorageState } from '../hooks/useLocalStorageState';

export type ExperienceMode = 'gentle' | 'structured';

type Ctx = {
  mode: ExperienceMode;
  setMode: (mode: ExperienceMode) => void;
};

const ExperienceModeContext = React.createContext<Ctx | null>(null);

export function ExperienceModeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useLocalStorageState<ExperienceMode>('lumen.experienceMode', 'gentle');
  return (
    <ExperienceModeContext.Provider value={{ mode, setMode }}>
      {children}
    </ExperienceModeContext.Provider>
  );
}

export function useExperienceMode() {
  const ctx = React.useContext(ExperienceModeContext);
  if (!ctx) {
    throw new Error('useExperienceMode must be used within ExperienceModeProvider');
  }
  return ctx;
}
