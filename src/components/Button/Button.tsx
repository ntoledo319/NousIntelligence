import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import styled, { css } from 'styled-components';
import { createRipple, rippleStyles } from '../../utils/ripple-effect';

// Types for icon positions
type IconPosition = 'left' | 'right';
type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'danger' | 'outline' | 'ghost';
type ButtonSize = 'small' | 'medium' | 'large';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * The variant of the button
   * @default 'primary'
   */
  variant?: ButtonVariant;
  /**
   * The size of the button
   * @default 'medium'
   */
  size?: ButtonSize;
  /**
   * If true, the button will take up the full width of its container
   * @default false
   */
  fullWidth?: boolean;
  /**
   * If true, the button will show a loading spinner
   * @default false
   */
  isLoading?: boolean;
  /**
   * The content to show when the button is in a loading state
   */
  loadingText?: string;
  /**
   * The position of the loading spinner
   * @default 'left'
   */
  loadingPosition?: IconPosition;
  /**
   * Icon to display - can be a React component or SVG
   */
  icon?: React.ReactNode;
  /**
   * Position of the icon relative to the text
   */
  iconPosition?: IconPosition;
  /**
   * Custom spinner component to override default loading spinner
   */
  spinner?: React.ReactNode;
  /**
   * Show tooltip when button is disabled
   */
  disabledTooltip?: string;
  /**
   * The content of the button
   */
  children: React.ReactNode;
}

interface Theme {
  colors: {
    primary: string;
    primaryDark: string;
    primaryLight: string;
    secondary: string;
    secondaryDark: string;
    secondaryLight: string;
    danger: string;
    dangerDark: string;
    dangerLight: string;
    text: string;
    textLight: string;
    textDisabled: string;
    white: string;
    black: string;
    gray: {
      300: string;
      500: string;
      700: string;
      800: string;
    };
  };
  spacing: {
    small: string;
    medium: string;
    large: string;
  };
  fonts: {
    body: string;
  };
  fontSizes: {
    sm: string;
    md: string;
    lg: string;
  };
  fontWeights: {
    medium: string;
  };
  lineHeights: {
    normal: string;
  };
  radii: {
    md: string;
  };
}

// Add ripple styles to global styles
const GlobalStyles = styled.div`
  ${rippleStyles}
`;

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  children,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  isLoading = false,
  loadingText,
  loadingPosition = 'left',
  icon,
  iconPosition = 'left',
  spinner,
  disabledTooltip,
  disabled = false,
  className = '',
  onClick,
  ...props
}, ref) => {
  const showIcon = !isLoading && icon;
  const showLoadingIcon = isLoading && (loadingPosition === iconPosition || !children);

  const renderIcon = () => {
    if (isLoading && showLoadingIcon) {
      return spinner || (
        <span className="button__loading">
          <span className="button__spinner" />
        </span>
      );
    }
    if (showIcon) {
      return (
        <span className="button__icon">
          {icon}
        </span>
      );
    }
    return null;
  };

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (onClick) {
      onClick(e);
    }
    
    if (!disabled && !isLoading) {
      createRipple(e, variant === 'primary' 
        ? 'rgba(255, 255, 255, 0.5)' 
        : 'rgba(0, 0, 0, 0.1)');
    }
  };

  return (
    <>
      <GlobalStyles />
      <StyledButton 
        ref={ref}
        type="button"
        className={`ripple-container button button--${variant} button--${size} ${
          fullWidth ? 'button--full-width' : ''
        } ${isLoading ? 'button--loading' : ''} ${className}`}
        disabled={disabled || isLoading}
        data-testid="button"
        data-variant={variant}
        data-size={size}
        aria-label={disabled && disabledTooltip ? disabledTooltip : undefined}
        aria-busy={isLoading}
        onClick={handleClick}
        {...props}
      >
        {(showLoadingIcon || (showIcon && iconPosition === 'left')) && renderIcon()}
        {isLoading && loadingText ? loadingText : children}
        {(showLoadingIcon || (showIcon && iconPosition === 'right')) && renderIcon()}
      </StyledButton>
    </>
  );
});

Button.displayName = 'Button';

const StyledButton = styled.button<ButtonProps>`
  ${({ theme, disabled, fullWidth, children }: { theme: Theme } & Pick<ButtonProps, 'disabled' | 'fullWidth' | 'children'>) => css`
    --button-bg: ${theme.colors.primary};
    --button-color: ${theme.colors.white};
    --button-hover-bg: ${theme.colors.primaryLight};
    --button-active-bg: ${theme.colors.primaryDark};
    --button-disabled-bg: ${theme.colors.gray[300]};
    --button-disabled-color: ${theme.colors.gray[500]};
    --button-border: none;
    --button-box-shadow: none;
    --button-padding: ${theme.spacing.medium} ${theme.spacing.large};
    --button-font-size: ${theme.fontSizes.md};
    --button-line-height: ${theme.lineHeights.normal};
    --button-border-radius: ${theme.radii.md};
    --button-transition: all 0.2s ease-in-out;
    width: ${fullWidth ? '100%' : 'auto'};
    opacity: ${disabled ? '0.7' : '1'};
    pointer-events: ${disabled ? 'none' : 'auto'};
    // Margin-right for loading and icon based on children
    .button__loading, .button__icon { margin-right: ${children ? '0.5rem' : '0'}; }
    // Variant and size styles can be handled via classes added in the component
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: relative;
    font-family: ${theme.fonts.body};
    font-weight: ${theme.fontWeights.medium};
    text-align: center;
    text-decoration: none;
    white-space: nowrap;
    vertical-align: middle;
    user-select: none;
    cursor: pointer;
    background-color: var(--button-bg);
    color: var(--button-color);
    border: var(--button-border);
    box-shadow: var(--button-box-shadow);
    padding: var(--button-padding);
    font-size: var(--button-font-size);
    line-height: var(--button-line-height);
    border-radius: var(--button-border-radius);
    transition: var(--button-transition);

    &:hover:not(:disabled) {
      background-color: var(--button-hover-bg);
      color: var(--button-color);
    }

    &:active:not(:disabled) {
      background-color: var(--button-active-bg);
      transform: translateY(1px);
    }

    &:disabled {
      cursor: not-allowed;
      background-color: var(--button-disabled-bg);
      color: var(--button-disabled-color);
    }

    /* Variants */
    &.button--secondary {
      --button-bg: ${theme.colors.secondary};
      --button-hover-bg: ${theme.colors.secondaryLight};
      --button-active-bg: ${theme.colors.secondaryDark};
    }

    &.button--danger {
      --button-bg: ${theme.colors.danger};
      --button-hover-bg: ${theme.colors.dangerLight};
      --button-active-bg: ${theme.colors.dangerDark};
    }

    &.button--outline {
      --button-bg: transparent;
      --button-color: ${theme.colors.primary};
      --button-hover-bg: ${theme.colors.primaryLight};
      --button-active-bg: ${theme.colors.primaryDark};
      --button-border: 1px solid currentColor;
    }

    &.button--ghost {
      --button-bg: transparent;
      --button-color: ${theme.colors.gray[700]};
      --button-hover-bg: ${theme.colors.gray[300]};
      --button-active-bg: ${theme.colors.gray[500]};
    }

    /* Sizes */
    &.button--small {
      --button-padding: ${theme.spacing.small} ${theme.spacing.medium};
      --button-font-size: ${theme.fontSizes.sm};
    }

    &.button--large {
      --button-padding: ${theme.spacing.large} ${theme.spacing.large};
      --button-font-size: ${theme.fontSizes.lg};
    }

    /* Loading state */
    .button__loading {
      display: inline-flex;
      align-items: center;
      margin-right: 0.5rem;
    }

    .button__spinner {
      width: 1em;
      height: 1em;
      border: 2px solid currentColor;
      border-bottom-color: transparent;
      border-radius: 50%;
      display: inline-block;
      box-sizing: border-box;
      animation: button-spin 1s linear infinite;
    }

    @keyframes button-spin {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }

    .button__icon {
      display: inline-flex;
      align-items: center;
      margin-right: 0.5rem;
    }

    &[data-icon-position='right'] .button__icon {
      margin-right: 0;
      margin-left: 0.5rem;
    }

    &[disabled] {
      position: relative;
      
      &::after {
        content: attr(aria-label);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: ${theme.colors.gray[800]};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
      }
      
      &:hover::after {
        opacity: 1;
      }
    }

    &:focus-visible {
      outline: 2px solid ${theme.colors.primary};
      outline-offset: 2px;
      box-shadow: 0 0 0 4px ${theme.colors.primaryLight};
    }
    
    /* Ripple container */
    &::after {
      content: '';
      display: block;
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      pointer-events: none;
      background-image: radial-gradient(circle, transparent 1%, transparent 1%);
      background-repeat: no-repeat;
      background-position: 50%;
      transform: scale(10, 10);
      opacity: 0;
      transition: transform 0.5s, opacity 1s;
    }
    
    &:active::after {
      transform: scale(0, 0);
      opacity: 0.3;
      transition: 0s;
    }
  `}
`;

export default Button;
