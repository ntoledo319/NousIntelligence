import React from 'react';
import styled from 'styled-components';
import Button from '../Button/Button';

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * The icon to display
   */
  icon: React.ReactNode;
  /**
   * The size of the button
   * @default 'medium'
   */
  size?: 'small' | 'medium' | 'large';
  /**
   * The variant of the button
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'tertiary' | 'danger' | 'outline' | 'ghost';
  /**
   * Accessible label for screen readers
   */
  ariaLabel: string;
}

const StyledIconButton = styled(Button)<IconButtonProps>`
  padding: ${({ size }) => 
    size === 'small' ? '0.25rem' : 
    size === 'large' ? '0.75rem' : 
    '0.5rem'
  };
  min-width: initial;
  width: ${({ size }) => 
    size === 'small' ? '2rem' : 
    size === 'large' ? '3rem' : 
    '2.5rem'
  };
  height: ${({ size }) => 
    size === 'small' ? '2rem' : 
    size === 'large' ? '3rem' : 
    '2.5rem'
  };
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
      data-testid="icon-button"
      {...props}
    >
      {icon}
    </StyledIconButton>
  );
};

export default IconButton;
