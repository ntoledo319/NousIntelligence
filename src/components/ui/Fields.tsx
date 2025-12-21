/**
 * Form field primitives for Lumen Harbor.
 *
 * @context_boundary UI primitives only
 * # AI-GENERATED 2025-12-21
 */
import styled from 'styled-components';

export const TextField = styled.input`
  width: 100%;
  border: 1px solid ${({ theme }) => theme.colors.border.subtle};
  border-radius: ${({ theme }) => theme.radii.md};
  padding: ${({ theme }) => theme.space[3]} ${({ theme }) => theme.space[4]};
  font: inherit;
  color: ${({ theme }) => theme.colors.text.default};
  background: ${({ theme }) => theme.colors.bg.elevated};

  &::placeholder {
    color: ${({ theme }) => theme.colors.text.subtle};
  }
`;

export const TextArea = styled.textarea`
  width: 100%;
  min-height: 140px;
  border: 1px solid ${({ theme }) => theme.colors.border.subtle};
  border-radius: ${({ theme }) => theme.radii.md};
  padding: ${({ theme }) => theme.space[3]} ${({ theme }) => theme.space[4]};
  font: inherit;
  color: ${({ theme }) => theme.colors.text.default};
  background: ${({ theme }) => theme.colors.bg.elevated};
  resize: vertical;

  &::placeholder {
    color: ${({ theme }) => theme.colors.text.subtle};
  }
`;
