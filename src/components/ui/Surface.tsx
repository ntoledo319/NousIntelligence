/**
 * Surface (layout primitive)
 *
 * Elevated card-like container. Used for primary content blocks.
 *
 * @context_boundary UI primitives only
 * # AI-GENERATED 2025-12-21
 */
import styled from 'styled-components';

export const Surface = styled.div`
  background: ${({ theme }) => theme.colors.bg.elevated};
  border: 1px solid ${({ theme }) => theme.colors.border.subtle};
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  padding: ${({ theme }) => theme.space[6]};
`;
