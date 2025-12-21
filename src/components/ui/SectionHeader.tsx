/**
 * SectionHeader (layout primitive)
 *
 * Consistent title/description block used at the top of pages and major sections.
 *
 * @context_boundary UI primitives only
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import styled from 'styled-components';

import { Inline } from './Inline';
import { Stack } from './Stack';

export interface SectionHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  as?: 'h1' | 'h2' | 'h3';
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  description,
  action,
  as = 'h2',
}) => {
  return (
    <Stack gap={2}>
      <Inline justify='space-between' align='baseline' wrap>
        <Title as={as}>{title}</Title>
        {action ? <ActionSlot>{action}</ActionSlot> : null}
      </Inline>
      {description ? <Description>{description}</Description> : null}
    </Stack>
  );
};

const Title = styled.h2`
  margin: 0;
  color: ${({ theme }) => theme.colors.text.strong};
  font-weight: ${({ theme }) => theme.typography.weights.semibold};
  line-height: ${({ theme }) => theme.typography.lineHeights.tight};
  font-size: ${({ theme }) => theme.typography.sizes.h2};
`;

const Description = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.text.muted};
  max-width: ${({ theme }) => theme.layout.contentMaxWidth};
`;

const ActionSlot = styled.div`
  flex: 0 0 auto;
`;
