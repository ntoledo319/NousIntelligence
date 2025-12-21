/**
 * Page (layout primitive)
 *
 * Full-height viewport container that:
 * - applies Lumen Harbor background
 * - constrains reading width
 * - reserves stable space for bottom navigation when requested
 *
 * @context_boundary UI primitives only
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import styled from 'styled-components';

export interface PageProps extends React.HTMLAttributes<HTMLElement> {
  /**
   * If true, adds bottom padding so content doesn't sit under mobile bottom-nav.
   */
  withNavPadding?: boolean;
  /**
   * If true, uses the comfortable reading measure (≈ 68ch).
   */
  narrow?: boolean;
}

export const Page: React.FC<React.PropsWithChildren<PageProps>> = ({
  withNavPadding = true,
  narrow = false,
  children,
  ...rest
}) => {
  return (
    <Root $withNavPadding={withNavPadding} {...rest}>
      <Content $narrow={narrow}>{children}</Content>
    </Root>
  );
};

const NAV_HEIGHT = 72;

const Root = styled.main<{ $withNavPadding: boolean }>`
  min-height: 100vh;
  background: ${({ theme }) => theme.colors.bg.main};
  padding: ${({ theme }) => theme.space[6]};
  padding-bottom: ${({ theme, $withNavPadding }) =>
    $withNavPadding ? `calc(${theme.space[6]} + ${NAV_HEIGHT}px)` : theme.space[6]};
`;

const Content = styled.div<{ $narrow: boolean }>`
  width: 100%;
  max-width: ${({ theme, $narrow }) =>
    $narrow ? theme.layout.contentMaxWidth : theme.layout.pageMaxWidth};
  margin: 0 auto;
`;
