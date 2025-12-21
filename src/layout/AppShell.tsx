/**
 * AppShell
 *
 * Hosts the persistent navigation and the Safety layer.
 * Pages render via `react-router` outlet.
 *
 * @context_boundary Layout only (no domain logic)
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import { LifebuoyIcon } from '@heroicons/react/24/outline';
import { Outlet } from 'react-router-dom';
import styled from 'styled-components';

import { SafetySheet } from '../components/safety/SafetySheet';

import { AppNav } from './AppNav';

export function AppShell() {
  const [safetyOpen, setSafetyOpen] = React.useState(false);

  return (
    <>
      <AppNav onOpenSafety={() => setSafetyOpen(true)} />
      <SafetyFab type='button' onClick={() => setSafetyOpen(true)}>
        <LifebuoyIcon width={18} height={18} aria-hidden='true' />
        <span>Need help now?</span>
      </SafetyFab>
      <Main>
        <Outlet />
      </Main>
      <SafetySheet open={safetyOpen} onClose={() => setSafetyOpen(false)} />
    </>
  );
}

const Main = styled.div`
  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    padding-left: 240px;
  }
`;

const SafetyFab = styled.button`
  position: fixed;
  right: ${({ theme }) => theme.space[4]};
  bottom: calc(72px + ${({ theme }) => theme.space[4]});
  z-index: 30;

  display: inline-flex;
  align-items: center;
  gap: ${({ theme }) => theme.space[2]};
  padding: ${({ theme }) => theme.space[3]} ${({ theme }) => theme.space[4]};
  border-radius: ${({ theme }) => theme.radii.pill};
  border: 1px solid ${({ theme }) => theme.colors.border.subtle};
  background: ${({ theme }) => theme.colors.bg.soft};
  color: ${({ theme }) => theme.colors.text.default};
  cursor: pointer;
  box-shadow: ${({ theme }) => theme.shadows.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    bottom: ${({ theme }) => theme.space[6]};
  }
`;
