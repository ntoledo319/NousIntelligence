import React from 'react';
import styled from 'styled-components';

interface ButtonGroupProps {
  /**
   * Direction of the buttons
   * @default 'row'
   */
  direction?: 'row' | 'column';
  /**
   * Spacing between buttons
   * @default 'medium'
   */
  spacing?: 'small' | 'medium' | 'large';
  /**
   * Whether buttons should be of equal width
   * @default false
   */
  equalWidth?: boolean;
  /**
   * Button elements
   */
  children: React.ReactNode;
}

const StyledButtonGroup = styled.div<ButtonGroupProps>`
  ${({ theme, direction = 'row', spacing = 'medium', equalWidth }) => `
    display: flex;
    flex-direction: ${direction};
    gap: ${theme.spacing[spacing]};
    width: 100%;

    ${equalWidth ? `
      & > * {
        flex: 1;
      }
    ` : ''}
  `}
`;

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  direction = 'row',
  spacing = 'medium',
  equalWidth = false,
}) => {
  return (
    <StyledButtonGroup 
      direction={direction}
      spacing={spacing}
      equalWidth={equalWidth}
      data-testid="button-group"
    >
      {children}
    </StyledButtonGroup>
  );
};

export default ButtonGroup;
