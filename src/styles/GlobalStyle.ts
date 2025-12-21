/**
 * Global styles for the Lumen Harbor UI.
 *
 * @context_boundary
 * - Owns baseline typography, colors, and accessibility defaults.
 * - Does NOT define component-level styling (use UI primitives instead).
 *
 * @ai_prompt "Keep global styles minimal, predictable, and WCAG-friendly.
 * Avoid surprise animations; respect prefers-reduced-motion."
 *
 * # AI-GENERATED 2025-12-21
 */
import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  *, *::before, *::after {
    box-sizing: border-box;
  }

  html, body {
    height: 100%;
  }

  body {
    margin: 0;
    font-family: ${({ theme }) => theme.typography.fontFamily};
    font-size: ${({ theme }) => theme.typography.sizes.body};
    line-height: ${({ theme }) => theme.typography.lineHeights.body};
    color: ${({ theme }) => theme.colors.text.default};
    background: ${({ theme }) => theme.colors.bg.main};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  a {
    color: ${({ theme }) => theme.colors.primary.strong};
    text-decoration-thickness: 0.08em;
    text-underline-offset: 0.18em;
  }

  a:hover {
    color: ${({ theme }) => theme.colors.primary.main};
  }

  ::selection {
    background: ${({ theme }) => theme.colors.primary.soft};
  }

  /* Predictable focus styling across the app */
  :focus-visible {
    outline: 2px solid ${({ theme }) => theme.colors.focus.ring};
    outline-offset: 2px;
    box-shadow: 0 0 0 4px ${({ theme }) => theme.colors.focus.ringSoft};
  }

  /* Reduce motion for safety and accessibility */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
`;
