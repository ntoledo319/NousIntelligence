/**
 * Frontend shell for the Limen Harbor UI demo.
 * @ai_prompt Use Limen Harbor theme tokens to keep CTA styles consistent.
 * @context_boundary React entry surface for the component gallery.
 * # TRAINING_DATA: internal-style-guide
 */

import React from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { ArrowRightIcon, ShieldCheckIcon, SparklesIcon } from '@heroicons/react/24/outline';
import Button from './components/Button';
import ButtonGroup from './components/ButtonGroup';
import IconButton from './components/IconButton';
import { theme, Theme } from './theme';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <AppShell>
        <HeroCard>
          <Pill>
            <SparklesIcon width={18} height={18} />
            AI-Powered Intelligence Platform
          </Pill>
          <Heading>
            Nous Intelligence
            <HeroAccent>Anchored in calm design</HeroAccent>
          </Heading>
          <Subheading>
            Limen Harbor provides a serene, trustworthy experience for cognitive workflows and
            decision support.
          </Subheading>
          <ButtonRow>
            <Button variant="primary" size="large" icon={<ArrowRightIcon width={18} height={18} />}>
              Launch Console
            </Button>
            <Button variant="outline" size="large">
              View Documentation
            </Button>
          </ButtonRow>
        </HeroCard>

        <SurfaceCard>
          <SectionHeader>
            <span>Component Sampler</span>
            <StatusBadge>
              <ShieldCheckIcon width={16} height={16} />
              Stable theme primitives
            </StatusBadge>
          </SectionHeader>
          <SectionCopy>
            Buttons, loading states, and icon affordances demonstrate the Limen Harbor aesthetic for
            primary and secondary actions.
          </SectionCopy>

          <ShowcaseGrid>
            <ShowcaseColumn>
              <Label>Variants</Label>
              <ButtonGroup spacing="small">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="danger">Danger</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
              </ButtonGroup>
            </ShowcaseColumn>

            <ShowcaseColumn>
              <Label>Sizes</Label>
              <ButtonGroup spacing="small">
                <Button size="small">Small</Button>
                <Button size="medium">Medium</Button>
                <Button size="large">Large</Button>
              </ButtonGroup>
            </ShowcaseColumn>

            <ShowcaseColumn>
              <Label>States</Label>
              <ButtonGroup spacing="small">
                <Button isLoading loadingText="Loading">
                  Loading
                </Button>
                <Button disabled disabledTooltip="This button is disabled">
                  Disabled
                </Button>
                <IconButton
                  ariaLabel="Quick action"
                  icon={<ArrowRightIcon width={18} height={18} />}
                  variant="secondary"
                />
              </ButtonGroup>
            </ShowcaseColumn>
          </ShowcaseGrid>
        </SurfaceCard>
      </AppShell>
    </ThemeProvider>
  );
};

const AppShell = styled.div(({ theme }: { theme: Theme }) => ({
  minHeight: '100vh',
  background: theme.gradients.calm,
  padding: theme.spacing.xl,
  fontFamily: theme.fonts.body,
  color: theme.colors.text,
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing.large,
}));

const HeroCard = styled.section(({ theme }: { theme: Theme }) => ({
  background: theme.gradients.hero,
  color: theme.colors.textInverse,
  borderRadius: theme.radii['2xl'],
  padding: theme.spacing.xxl,
  boxShadow: theme.shadows.xl,
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing.medium,
}));

const SurfaceCard = styled.section(({ theme }: { theme: Theme }) => ({
  background: theme.gradients.card,
  borderRadius: theme.radii.xl,
  padding: theme.spacing.xl,
  boxShadow: theme.shadows.lg,
  border: `1px solid ${theme.colors.border}`,
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing.medium,
}));

const Heading = styled.h1(({ theme }: { theme: Theme }) => ({
  fontSize: theme.fontSizes['3xl'],
  fontWeight: theme.fontWeights.bold,
  margin: 0,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing.small,
  flexWrap: 'wrap',
}));

const HeroAccent = styled.span(({ theme }: { theme: Theme }) => ({
  fontSize: theme.fontSizes.md,
  fontWeight: theme.fontWeights.medium,
  background: theme.gradients.accent,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
}));

const Subheading = styled.p(({ theme }: { theme: Theme }) => ({
  margin: 0,
  maxWidth: '42rem',
  lineHeight: theme.lineHeights.relaxed,
  fontSize: theme.fontSizes.lg,
  color: theme.colors.textLight,
}));

const Pill = styled.span(({ theme }: { theme: Theme }) => ({
  display: 'inline-flex',
  alignItems: 'center',
  gap: theme.spacing.small,
  padding: `${theme.spacing.small} ${theme.spacing.medium}`,
  backgroundColor: 'rgba(255,255,255,0.16)',
  borderRadius: theme.radii.full,
  fontSize: theme.fontSizes.sm,
  fontWeight: theme.fontWeights.medium,
  letterSpacing: '0.01em',
  width: 'fit-content',
}));

const ButtonRow = styled.div(({ theme }: { theme: Theme }) => ({
  display: 'flex',
  gap: theme.spacing.medium,
  flexWrap: 'wrap',
}));

const SectionHeader = styled.div(({ theme }: { theme: Theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  gap: theme.spacing.medium,
  flexWrap: 'wrap',
  fontSize: theme.fontSizes.lg,
  fontWeight: theme.fontWeights.semibold,
  color: theme.colors.text,
}));

const SectionCopy = styled.p(({ theme }: { theme: Theme }) => ({
  margin: 0,
  color: theme.colors.textLight,
  lineHeight: theme.lineHeights.relaxed,
}));

const StatusBadge = styled.span(({ theme }: { theme: Theme }) => ({
  display: 'inline-flex',
  alignItems: 'center',
  gap: theme.spacing.small,
  padding: `${theme.spacing.small} ${theme.spacing.medium}`,
  backgroundColor: theme.colors.background,
  color: theme.colors.text,
  borderRadius: theme.radii.full,
  border: `1px solid ${theme.colors.border}`,
  boxShadow: theme.shadows.sm,
  fontSize: theme.fontSizes.sm,
}));

const ShowcaseGrid = styled.div(({ theme }: { theme: Theme }) => ({
  display: 'grid',
  gap: theme.spacing.large,
  gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
}));

const ShowcaseColumn = styled.div(({ theme }: { theme: Theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing.small,
  padding: theme.spacing.medium,
  borderRadius: theme.radii.md,
  backgroundColor: theme.colors.surface,
  boxShadow: theme.shadows.sm,
  border: `1px solid ${theme.colors.border}`,
}));

const Label = styled.span(({ theme }: { theme: Theme }) => ({
  fontSize: theme.fontSizes.sm,
  fontWeight: theme.fontWeights.semibold,
  color: theme.colors.text,
  letterSpacing: '0.02em',
  textTransform: 'uppercase',
}));

export default App;
