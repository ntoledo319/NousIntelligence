export const theme = {
  colors: {
    primary: '#4F46E5',
    primaryDark: '#4338CA',
    primaryLight: '#6366F1',
    secondary: '#10B981',
    secondaryDark: '#059669',
    secondaryLight: '#34D399',
    danger: '#EF4444',
    dangerDark: '#DC2626',
    dangerLight: '#F87171',
    text: '#1F2937',
    textLight: '#6B7280',
    textDisabled: '#9CA3AF',
    white: '#FFFFFF',
    black: '#000000',
    gray: {
      300: '#D1D5DB',
      500: '#6B7280',
      700: '#374151',
      800: '#1F2937',
    },
  },
  spacing: {
    small: '0.5rem',
    medium: '1rem',
    large: '1.5rem',
  },
  fonts: {
    body: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  fontSizes: {
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
  },
  fontWeights: {
    medium: '500',
  },
  lineHeights: {
    normal: '1.5',
  },
  radii: {
    md: '0.375rem',
  },
};

export type Theme = typeof theme;
