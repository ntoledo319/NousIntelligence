/**
 * Lumen Harbor Theme Tokens
 * @context_boundary Frontend UI theme tokens only (no backend coupling)
 *
 * - Use semantic tokens in components (e.g., `theme.colors.text.muted`).
 * - Avoid hard-coded hex values outside this file.
 *
 * @ai_prompt "Apply Lumen Harbor tokens; prefer semantic colors and spacing.
 * Keep UI calm, predictable, and trauma-aware."
 *
 * # AI-GENERATED 2025-12-21
 * # ORIGINAL_INTENT: Replace ad-hoc demo theme with Lumen Harbor system tokens.
 * ## Non-Negotiables
 * - No raw hex use in components (semantic tokens only)
 * - Provide visible focus states and reduced-motion defaults
 */
export const theme = {
  colors: {
    bg: {
      main: '#F9FAFB',
      elevated: '#FFFFFF',
      soft: '#E5F1F3',
    },
    text: {
      strong: '#0F172A',
      default: '#111827',
      muted: '#6B7280',
      subtle: '#9CA3AF',
      inverse: '#FFFFFF',
    },
    primary: {
      main: '#0D9488',
      soft: '#CCF3ED',
      strong: '#0F766E',
    },
    secondary: {
      main: '#4F46E5',
      soft: '#E0E7FF',
    },
    accent: {
      warm: '#FDBA74',
      softRose: '#FCE7F3',
    },
    semantic: {
      success: '#22C55E',
      info: '#38BDF8',
      warning: '#F59E0B',
      danger: '#DC2626',
    },
    border: {
      subtle: '#E5E7EB',
      strong: '#CBD5E1',
    },
    shadow: {
      color: 'rgba(15, 23, 42, 0.10)',
    },
    focus: {
      ring: '#38BDF8',
      ringSoft: 'rgba(56, 189, 248, 0.35)',
    },
  },
  typography: {
    fontFamily:
      'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Segoe UI", sans-serif',
    sizes: {
      body: '1rem', // 16px baseline (mobile-first)
      bodyLg: '1.125rem', // 18px
      small: '0.875rem', // 14px
      h1: '1.75rem', // 28px
      h2: '1.375rem', // 22px
      h3: '1.125rem', // 18px
    },
    weights: {
      regular: 400,
      medium: 500,
      semibold: 600,
    },
    lineHeights: {
      body: 1.6,
      tight: 1.25,
    },
    measure: {
      comfortable: '68ch',
    },
  },
  space: {
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    8: '2rem',
    10: '2.5rem',
    12: '3rem',
    16: '4rem',
  },
  radii: {
    sm: '0.5rem',
    md: '0.75rem',
    lg: '1rem',
    pill: '9999px',
  },
  shadows: {
    sm: '0 1px 2px rgba(15, 23, 42, 0.06)',
    md: '0 6px 18px rgba(15, 23, 42, 0.08)',
  },
  layout: {
    pageMaxWidth: '1100px',
    contentMaxWidth: '68ch',
  },
  breakpoints: {
    sm: '480px',
    md: '768px',
    lg: '1024px',
  },
} as const;

export type Theme = typeof theme;
