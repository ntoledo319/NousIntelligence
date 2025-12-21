import React from 'react';

import styled from 'styled-components';

import Button, { type ButtonProps } from '../Button/Button';

interface IconButtonProps extends Omit<ButtonProps, 'children' | 'icon'> {
  /**
   * The icon to display.
   */
  icon: React.ReactNode;
  /**
   * Accessible label for screen readers.
   */
  ariaLabel: string;
}

type StyledIconButtonProps = Omit<IconButtonProps, 'icon' | 'ariaLabel'>;

const StyledIconButton = styled(Button)<StyledIconButtonProps>`
  padding: ${({ size }) => {
    const map = {
      small: '0.25rem',
      medium: '0.5rem',
      large: '0.75rem',
    } as const;
    return map[size ?? 'medium'];
  }};
  min-width: initial;
  width: ${({ size }) => {
    const map = {
      small: '2rem',
      medium: '2.5rem',
      large: '3rem',
    } as const;
    return map[size ?? 'medium'];
  }};
  height: ${({ size }) => {
    const map = {
      small: '2rem',
      medium: '2.5rem',
      large: '3rem',
    } as const;
    return map[size ?? 'medium'];
  }};
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
`;

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  size = 'medium',
  variant = 'primary',
  ariaLabel,
  ...props
}) => {
  return (
    <StyledIconButton
      size={size}
      variant={variant}
      aria-label={ariaLabel}
      data-testid='icon-button'
      {...props}
    >
      {icon}
    </StyledIconButton>
  );
};

export default IconButton;
