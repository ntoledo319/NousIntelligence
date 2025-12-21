/**
 * useLocalStorageState
 *
 * Tiny helper for storing simple UI preferences (e.g., experience mode).
 *
 * @context_boundary Frontend-only (no backend coupling)
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

export function useLocalStorageState<T>(key: string, initialValue: T) {
  const [value, setValue] = React.useState<T>(() => {
    try {
      const raw = window.localStorage.getItem(key);
      if (raw == null) return initialValue;
      return JSON.parse(raw) as T;
    } catch {
      return initialValue;
    }
  });

  React.useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Ignore storage failures (private mode, quota, etc).
    }
  }, [key, value]);

  return [value, setValue] as const;
}
