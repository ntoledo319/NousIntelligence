/**
 * Stack (layout primitive)
 *
 * A small, predictable vertical layout helper used across Lumen Harbor screens.
 * Avoids ad-hoc margins and keeps spacing consistent with theme tokens.
 *
 * @context_boundary UI primitives only
 * @ai_prompt "Use Stack/Inline primitives instead of random margins."
 *
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import styled from 'styled-components';

type SpaceKey = keyof import('../../theme').Theme['space'];

export interface StackProps extends React.HTMLAttributes<HTMLDivElement> {
  gap?: SpaceKey;
  align?: React.CSSProperties['alignItems'];
}

export const Stack: React.FC<React.PropsWithChildren<StackProps>> = ({
  gap = 4,
  align,
  children,
  ...rest
}) => {
  return (
    <Root
      $gap={gap}
      style={align ? { alignItems: align, ...(rest.style ?? {}) } : rest.style}
      {...rest}
    >
      {children}
    </Root>
  );
};

const Root = styled.div<{ $gap: SpaceKey }>`
  display: flex;
  flex-direction: column;
  gap: ${({ theme, $gap }) => theme.space[$gap]};
`;
