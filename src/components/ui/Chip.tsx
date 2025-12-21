/**
 * Chip (toggle pill)
 *
 * Used for low-cognitive-load tagging and quick filters.
 * Uses `aria-pressed` for accessibility.
 *
 * @context_boundary UI primitives only
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import styled from 'styled-components';

export interface ChipProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean;
}

export const Chip: React.FC<React.PropsWithChildren<ChipProps>> = ({
  selected = false,
  children,
  ...rest
}) => {
  return (
    <Root type='button' aria-pressed={selected} $selected={selected} {...rest}>
      {children}
    </Root>
  );
};

const Root = styled.button<{ $selected: boolean }>`
  border: 1px solid
    ${({ theme, $selected }) =>
      $selected ? theme.colors.primary.main : theme.colors.border.subtle};
  background: ${({ theme, $selected }) =>
    $selected ? theme.colors.primary.soft : theme.colors.bg.elevated};
  color: ${({ theme }) => theme.colors.text.default};
  border-radius: ${({ theme }) => theme.radii.pill};
  padding: ${({ theme }) => theme.space[2]} ${({ theme }) => theme.space[3]};
  font: inherit;
  font-size: ${({ theme }) => theme.typography.sizes.small};
  cursor: pointer;
  transition: background 160ms ease, border-color 160ms ease;
`;
