/**
 * NOUS Theme System - Limen Harbor
 * 
 * A calming, nautical-inspired design language for mental wellness applications.
 * Limen Harbor represents a safe haven - a threshold between storm and calm,
 * designed to provide comfort and serenity for users on their mental health journey.
 * 
 * @ai_prompt Use Limen Harbor theme colors for a calming, therapeutic UI
 * @context_boundary Theme system for React components
 */

export const theme = {
  colors: {
    // Primary Harbor Blues - Calm, trustworthy, therapeutic
    primary: '#0891b2', // Cyan-600: Harbor water
    primaryDark: '#0e7490', // Cyan-700: Deeper waters
    primaryLight: '#22d3ee', // Cyan-400: Surface reflection
    primarySoft: '#a5f3fc', // Cyan-200: Morning mist
    
    // Secondary Seafoam - Tranquility and growth
    secondary: '#14b8a6', // Teal-500: Seafoam
    secondaryDark: '#0d9488', // Teal-600: Deep seafoam
    secondaryLight: '#5eead4', // Teal-300: Light spray
    
    // Semantic Colors
    danger: '#dc2626', // Red-600: Warning buoy
    dangerDark: '#b91c1c',
    dangerLight: '#f87171',
    
    success: '#059669', // Emerald-600: Safe passage
    successLight: '#10b981',
    
    warning: '#d97706', // Amber-600: Lighthouse
    warningLight: '#f59e0b',
    
    info: '#0284c7', // Sky-600: Clear skies
    infoLight: '#0ea5e9',
    
    // Text Colors - Clear visibility
    text: '#134e4a', // Teal-900: Deep navigation
    textLight: '#115e59', // Teal-800: Harbor signs
    textMuted: '#5eead4', // Teal-300: Distant shore
    textDisabled: '#99f6e4', // Teal-200: Faded
    textInverse: '#ffffff', // White: Light signals
    
    // Neutral Colors
    white: '#ffffff',
    black: '#000000',
    
    // Surface Colors
    background: '#f0fdfa', // Teal-50: Harbor fog
    backgroundSoft: '#f8fafc', // Slate-50: Soft sky
    surface: '#ffffff', // White: Clean decks
    surfaceHover: '#ecfeff', // Cyan-50: Touched by water
    
    // Border Colors
    border: '#99f6e4', // Teal-200: Water's edge
    borderHover: '#5eead4', // Teal-300: Ripple
    borderFocus: '#0891b2', // Cyan-600: Focus beacon
    
    gray: {
      50: '#f0fdfa',
      100: '#ccfbf1',
      200: '#99f6e4',
      300: '#5eead4',
      400: '#2dd4bf',
      500: '#14b8a6',
      600: '#0d9488',
      700: '#0f766e',
      800: '#115e59',
      900: '#134e4a',
    },
  },
  
  // Limen Harbor Gradients
  gradients: {
    hero: 'linear-gradient(135deg, #0891b2 0%, #14b8a6 50%, #0284c7 100%)',
    heroAlt: 'linear-gradient(135deg, #155e75 0%, #0891b2 50%, #0ea5e9 100%)',
    button: 'linear-gradient(135deg, #0891b2 0%, #14b8a6 100%)',
    buttonHover: 'linear-gradient(135deg, #0e7490 0%, #0d9488 100%)',
    accent: 'linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%)',
    calm: 'linear-gradient(180deg, #ecfeff 0%, #f0fdfa 50%, #f0f9ff 100%)',
    surface: 'linear-gradient(135deg, rgba(240, 253, 250, 0.95) 0%, rgba(236, 254, 255, 0.9) 100%)',
    card: 'linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 253, 250, 0.95) 100%)',
  },
  
  spacing: {
    xs: '0.25rem',
    small: '0.5rem',
    medium: '1rem',
    large: '1.5rem',
    xl: '2rem',
    xxl: '3rem',
  },
  
  fonts: {
    body: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  },
  
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
  },
  
  fontWeights: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
  
  lineHeights: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.75',
  },
  
  radii: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    full: '9999px',
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgba(8, 145, 178, 0.05)',
    md: '0 4px 6px -1px rgba(8, 145, 178, 0.1), 0 2px 4px -1px rgba(8, 145, 178, 0.06)',
    lg: '0 10px 15px -3px rgba(8, 145, 178, 0.1), 0 4px 6px -2px rgba(8, 145, 178, 0.05)',
    xl: '0 20px 25px -5px rgba(8, 145, 178, 0.1), 0 10px 10px -5px rgba(8, 145, 178, 0.04)',
    '2xl': '0 25px 50px -12px rgba(8, 145, 178, 0.25)',
  },
  
  transitions: {
    fast: '0.15s ease-out',
    normal: '0.3s ease-out',
    slow: '0.5s ease-out',
  },
  
  // Semantic tokens for component usage
  semantic: {
    focus: {
      ring: '0 0 0 3px rgba(8, 145, 178, 0.15)',
      borderColor: '#0891b2',
    },
    hover: {
      scale: 'scale(1.02)',
      translateY: 'translateY(-2px)',
    },
  },
};

export type Theme = typeof theme;

/**
 * Limen Harbor Dark Theme Variant
 * For users who prefer dark mode or low-light environments
 */
export const darkTheme: Theme = {
  ...theme,
  colors: {
    ...theme.colors,
    primary: '#22d3ee', // Cyan-400: Moonlit waters
    primaryDark: '#06b6d4', // Cyan-500: Deep night
    primaryLight: '#67e8f9', // Cyan-300: Starlight on water
    primarySoft: '#0891b2', // Cyan-600: Distant glow
    
    secondary: '#5eead4', // Teal-300: Bioluminescence
    secondaryDark: '#2dd4bf', // Teal-400: Glowing foam
    secondaryLight: '#99f6e4', // Teal-200: Light spray
    
    text: '#f0fdfa', // Teal-50: Lighthouse beam
    textLight: '#ccfbf1', // Teal-100: Soft glow
    textMuted: '#5eead4', // Teal-300: Distant light
    textInverse: '#042f2e', // Teal-950: Dark inverse
    
    background: '#042f2e', // Teal-950: Deep night harbor
    backgroundSoft: '#083344', // Cyan-950: Night sky
    surface: '#134e4a', // Teal-900: Harbor deck
    surfaceHover: '#115e59', // Teal-800: Moonlit deck
    
    border: '#115e59', // Teal-800: Night edge
    borderHover: '#14b8a6', // Teal-500: Active edge
    borderFocus: '#22d3ee', // Cyan-400: Focus beacon
    
    gray: {
      50: '#042f2e',
      100: '#134e4a',
      200: '#115e59',
      300: '#0f766e',
      400: '#0d9488',
      500: '#14b8a6',
      600: '#2dd4bf',
      700: '#5eead4',
      800: '#99f6e4',
      900: '#ccfbf1',
    },
  },
  gradients: {
    ...theme.gradients,
    hero: 'linear-gradient(135deg, #155e75 0%, #134e4a 50%, #083344 100%)',
    heroAlt: 'linear-gradient(135deg, #164e63 0%, #115e59 50%, #134e4a 100%)',
    card: 'linear-gradient(135deg, rgba(20, 78, 74, 0.95) 0%, rgba(17, 94, 89, 0.9) 100%)',
  },
  shadows: {
    ...theme.shadows,
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)',
    xl: '0 20px 25px -5px rgba(6, 182, 212, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.3)',
    '2xl': '0 25px 50px -12px rgba(6, 182, 212, 0.25)',
  },
};

export default theme;
