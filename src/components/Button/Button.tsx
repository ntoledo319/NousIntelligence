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

// Add ripple styles to global styles
const GlobalStyles = styled.div`
  ${rippleStyles}
`;

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
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
    },
    ref
  ) => {
    const showIcon = !isLoading && icon;
    const showLoadingIcon = isLoading && (loadingPosition === iconPosition || !children);

    const renderIcon = () => {
      if (isLoading && showLoadingIcon) {
        return (
          spinner || (
            <span className='button__loading'>
              <span className='button__spinner' />
            </span>
          )
        );
      }
      if (showIcon) {
        return <span className='button__icon'>{icon}</span>;
      }
      return null;
    };

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (onClick) {
        onClick(e);
      }

      if (!disabled && !isLoading) {
        createRipple(e, variant === 'primary' ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.1)');
      }
    };

    return (
      <>
        <GlobalStyles />
        <StyledButton
          ref={ref}
          type='button'
          className={`ripple-container button button--${variant} button--${size} ${
            fullWidth ? 'button--full-width' : ''
          } ${isLoading ? 'button--loading' : ''} ${className}`}
          disabled={disabled || isLoading}
          data-testid='button'
          data-variant={variant}
          data-size={size}
          aria-label={disabled && disabledTooltip ? disabledTooltip : undefined}
          aria-busy={isLoading}
          onClick={handleClick}
          {...props}
        >
          {(showLoadingIcon || (showIcon && iconPosition === 'left')) && renderIcon()}
          <span className='button__label'>{isLoading && loadingText ? loadingText : children}</span>
          {(showLoadingIcon || (showIcon && iconPosition === 'right')) && renderIcon()}
        </StyledButton>
      </>
    );
  }
);

Button.displayName = 'Button';

const StyledButton = styled.button<ButtonProps>`
  ${({ theme, disabled, fullWidth }) => css`
    --button-bg: ${theme.colors.primary.main};
    --button-color: ${theme.colors.text.inverse};
    --button-hover-bg: ${theme.colors.primary.strong};
    --button-active-bg: ${theme.colors.primary.strong};
    --button-disabled-bg: ${theme.colors.bg.soft};
    --button-disabled-color: ${theme.colors.text.subtle};
    --button-border: none;
    --button-box-shadow: none;
    --button-padding: ${theme.space[3]} ${theme.space[4]};
    --button-font-size: ${theme.typography.sizes.body};
    --button-line-height: ${theme.typography.lineHeights.tight};
    --button-border-radius: ${theme.radii.md};
    --button-transition: all 0.2s ease-in-out;
    width: ${fullWidth ? '100%' : 'auto'};
    opacity: ${disabled ? '0.7' : '1'};
    pointer-events: ${disabled ? 'none' : 'auto'};
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: ${theme.space[2]};
    position: relative;
    font-family: ${theme.typography.fontFamily};
    font-weight: ${theme.typography.weights.medium};
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
      --button-bg: ${theme.colors.secondary.main};
      --button-hover-bg: ${theme.colors.secondary.main};
      --button-active-bg: ${theme.colors.secondary.main};
    }

    &.button--danger {
      --button-bg: ${theme.colors.semantic.danger};
      --button-hover-bg: ${theme.colors.semantic.danger};
      --button-active-bg: ${theme.colors.semantic.danger};
    }

    &.button--outline {
      --button-bg: transparent;
      --button-color: ${theme.colors.primary.strong};
      --button-hover-bg: ${theme.colors.primary.soft};
      --button-active-bg: ${theme.colors.primary.soft};
      --button-border: 1px solid currentColor;
    }

    &.button--ghost {
      --button-bg: transparent;
      --button-color: ${theme.colors.text.muted};
      --button-hover-bg: ${theme.colors.bg.soft};
      --button-active-bg: ${theme.colors.bg.soft};
    }

    /* Sizes */
    &.button--small {
      --button-padding: ${theme.space[2]} ${theme.space[3]};
      --button-font-size: ${theme.typography.sizes.small};
    }

    &.button--large {
      --button-padding: ${theme.space[4]} ${theme.space[4]};
      --button-font-size: ${theme.typography.sizes.bodyLg};
    }

    /* Loading state */
    .button__loading {
      display: inline-flex;
      align-items: center;
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
        background: ${theme.colors.text.strong};
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
      outline: 2px solid ${theme.colors.focus.ring};
      outline-offset: 2px;
      box-shadow: 0 0 0 4px ${theme.colors.focus.ringSoft};
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
export type { ButtonProps };
