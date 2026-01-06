/**
 * NOUS Theme System - Sanctuary (Hygge Haven)
 * 
 * A therapeutic, emotionally resonant design language rooted in "calm technology".
 * Inspired by wabi-sabi, nesting, and organic warmth.
 * 
 * @ai_prompt Use Sanctuary theme colors for a therapeutic, lived-in UI
 * @context_boundary Theme system for React components
 */

export const theme = {
  colors: {
    // Primary: Sage & Eucalyptus - Healing, grounded nature
    primary: '#8da399', // Sage Green
    primaryDark: '#6b8278', // Deep Sage
    primaryLight: '#b4c5bc', // Light Sage
    primarySoft: '#d8e2dd', // Mist

    // Secondary: Warm Sand & Clay - Earthy comfort
    secondary: '#d6cbb6', // Warm Sand
    secondaryDark: '#b5aa94', // Dark Sand
    secondaryLight: '#e8e1d3', // Light Sand

    // Semantic Colors - Muted, non-alarming
    danger: '#c8553d', // Terracotta/Rust (instead of bright red)
    dangerDark: '#a0402c',
    dangerLight: '#eebbb1',
    
    success: '#588157', // Forest Green (instead of neon green)
    successLight: '#8dbe8b',
    
    warning: '#e09f3e', // Goldenrod (instead of bright orange)
    warningLight: '#f4d098',
    
    info: '#648dae', // Slate Blue (instead of bright blue)
    infoLight: '#a3c2d9',
    
    // Text Colors - Soft contrast
    text: '#4a4a4a', // Soft Charcoal (never pure black)
    textLight: '#6e6e6e', // Warm Grey
    textMuted: '#949494', // Stone
    textDisabled: '#c7c7c7', // Pebble
    textInverse: '#fdfcf8', // Rice Paper
    
    // Neutral Colors
    white: '#ffffff',
    black: '#000000',
    
    // Surface Colors - Paper-like, warm
    background: '#fdfcf8', // Rice Paper / Cream
    backgroundSoft: '#f7f5f0', // Warm Linen
    surface: '#ffffff',
    surfaceHover: '#f9f8f6',
    
    // Border Colors - Soft definition
    border: '#e6e2d8', // Parchment
    borderHover: '#d6cbb6', // Sand
    borderFocus: '#8da399', // Sage
    
    gray: {
      50: '#f9f8f6',
      100: '#f2efe9',
      200: '#e6e2d8',
      300: '#d6cbb6',
      400: '#bcb099',
      500: '#a39780',
      600: '#8a7f6b',
      700: '#706756',
      800: '#575043',
      900: '#3d382f',
    },
  },
  
  // Organic Gradients
  gradients: {
    hero: 'linear-gradient(135deg, #fdfcf8 0%, #f2efe9 100%)',
    heroAlt: 'linear-gradient(135deg, #e8e1d3 0%, #d6cbb6 100%)',
    button: 'linear-gradient(135deg, #8da399 0%, #7a9187 100%)',
    buttonHover: 'linear-gradient(135deg, #6b8278 0%, #5d7369 100%)',
    accent: 'linear-gradient(135deg, #d6cbb6 0%, #c5baab 100%)',
    calm: 'linear-gradient(180deg, #fdfcf8 0%, #f7f5f0 100%)',
    surface: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(253, 252, 248, 0.8) 100%)',
    card: 'linear-gradient(135deg, #ffffff 0%, #fdfcf8 100%)',
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
    heading: "'Lora', serif",
    body: "'Nunito', sans-serif",
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
    normal: '1.6', // Increased for readability/calm
    relaxed: '1.8',
  },
  
  radii: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    '2xl': '1.5rem',
    full: '9999px',
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgba(163, 151, 128, 0.05)',
    md: '0 4px 6px -1px rgba(163, 151, 128, 0.1), 0 2px 4px -1px rgba(163, 151, 128, 0.06)',
    lg: '0 10px 15px -3px rgba(163, 151, 128, 0.1), 0 4px 6px -2px rgba(163, 151, 128, 0.05)',
    xl: '0 20px 25px -5px rgba(163, 151, 128, 0.1), 0 10px 10px -5px rgba(163, 151, 128, 0.04)',
    '2xl': '0 25px 50px -12px rgba(163, 151, 128, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.02)',
  },
  
  transitions: {
    fast: '0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    normal: '0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '0.5s cubic-bezier(0.4, 0, 0.2, 1)',
  },
  
  // Semantic tokens for component usage
  semantic: {
    focus: {
      ring: '0 0 0 3px rgba(141, 163, 153, 0.2)',
      borderColor: '#8da399',
    },
    hover: {
      scale: 'scale(1.01)', // More subtle
      translateY: 'translateY(-1px)',
    },
  },
};

export type Theme = typeof theme;

/**
 * Sanctuary Dark Theme Variant
 * Warm, cozy night mode (not pitch black)
 */
export const darkTheme: Theme = {
  ...theme,
  colors: {
    ...theme.colors,
    primary: '#8da399', // Sage
    primaryDark: '#6b8278',
    primaryLight: '#b4c5bc',
    primarySoft: '#3d4a44', 
    
    secondary: '#bcb099',
    secondaryDark: '#a39780',
    secondaryLight: '#d6cbb6',
    
    text: '#f2efe9', // Parchment White
    textLight: '#e6e2d8',
    textMuted: '#a39780',
    textInverse: '#3d382f',
    
    background: '#2c2a26', // Dark Walnut/Espresso (warm dark)
    backgroundSoft: '#36332e', // Lighter Walnut
    surface: '#3d382f', // Dark Oak
    surfaceHover: '#454036',
    
    border: '#454036',
    borderHover: '#575043',
    borderFocus: '#8da399',
    
    gray: {
      50: '#2c2a26',
      100: '#3d382f',
      200: '#454036',
      300: '#575043',
      400: '#706756',
      500: '#8a7f6b',
      600: '#a39780',
      700: '#bcb099',
      800: '#d6cbb6',
      900: '#e6e2d8',
    },
  },
  gradients: {
    ...theme.gradients,
    hero: 'linear-gradient(135deg, #2c2a26 0%, #36332e 100%)',
    heroAlt: 'linear-gradient(135deg, #3d382f 0%, #454036 100%)',
    card: 'linear-gradient(135deg, #3d382f 0%, #36332e 100%)',
  },
  shadows: {
    ...theme.shadows,
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.3)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
  },
};

export default theme;
