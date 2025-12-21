/**
 * Inline (layout primitive)
 *
 * Horizontal spacing helper with predictable gaps and optional wrapping.
 *
 * @context_boundary UI primitives only
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import styled from 'styled-components';

type SpaceKey = keyof import('../../theme').Theme['space'];

export interface InlineProps extends React.HTMLAttributes<HTMLDivElement> {
  gap?: SpaceKey;
  align?: React.CSSProperties['alignItems'];
  justify?: React.CSSProperties['justifyContent'];
  wrap?: boolean;
}

export const Inline: React.FC<React.PropsWithChildren<InlineProps>> = ({
  gap = 3,
  align,
  justify,
  wrap = false,
  children,
  ...rest
}) => {
  return (
    <Root
      $gap={gap}
      $wrap={wrap}
      style={{
        ...(align ? { alignItems: align } : {}),
        ...(justify ? { justifyContent: justify } : {}),
        ...(rest.style ?? {}),
      }}
      {...rest}
    >
      {children}
    </Root>
  );
};

const Root = styled.div<{ $gap: SpaceKey; $wrap: boolean }>`
  display: flex;
  flex-direction: row;
  gap: ${({ theme, $gap }) => theme.space[$gap]};
  flex-wrap: ${({ $wrap }) => ($wrap ? 'wrap' : 'nowrap')};
`;
