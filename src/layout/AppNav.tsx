/**
 * AppNav (Harbor navigation)
 *
 * Mobile-first navigation:
 * - Bottom nav on small screens
 * - Left rail on desktop
 *
 * @context_boundary Layout + navigation only (no data fetching)
 * # AI-GENERATED 2025-12-21
 */
import {
  ChatBubbleLeftRightIcon,
  EllipsisHorizontalCircleIcon,
  HeartIcon,
  HomeIcon,
  PencilSquareIcon,
  LifebuoyIcon,
} from '@heroicons/react/24/outline';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';

export interface AppNavProps {
  onOpenSafety: () => void;
}

export function AppNav({ onOpenSafety }: AppNavProps) {
  return (
    <>
      <MobileNav aria-label='Primary navigation'>
        <NavItem to='/' end>
          <HomeIcon width={22} height={22} aria-hidden='true' />
          <span>Home</span>
        </NavItem>
        <NavItem to='/mood'>
          <HeartIcon width={22} height={22} aria-hidden='true' />
          <span>Mood</span>
        </NavItem>
        <NavItem to='/journal'>
          <PencilSquareIcon width={22} height={22} aria-hidden='true' />
          <span>Journal</span>
        </NavItem>
        <NavItem to='/talk'>
          <ChatBubbleLeftRightIcon width={22} height={22} aria-hidden='true' />
          <span>Talk</span>
        </NavItem>
        <NavItem to='/more'>
          <EllipsisHorizontalCircleIcon width={22} height={22} aria-hidden='true' />
          <span>More</span>
        </NavItem>
      </MobileNav>

      <DesktopNav aria-label='Primary navigation'>
        <Brand>NOUS</Brand>
        <Rail>
          <RailItem to='/' end>
            <HomeIcon width={20} height={20} aria-hidden='true' />
            <span>Harbor</span>
          </RailItem>
          <RailItem to='/mood'>
            <HeartIcon width={20} height={20} aria-hidden='true' />
            <span>Mood</span>
          </RailItem>
          <RailItem to='/journal'>
            <PencilSquareIcon width={20} height={20} aria-hidden='true' />
            <span>Journal</span>
          </RailItem>
          <RailItem to='/talk'>
            <ChatBubbleLeftRightIcon width={20} height={20} aria-hidden='true' />
            <span>Talk</span>
          </RailItem>
          <RailItem to='/more'>
            <EllipsisHorizontalCircleIcon width={20} height={20} aria-hidden='true' />
            <span>More</span>
          </RailItem>
        </Rail>

        <SafetyButton type='button' onClick={onOpenSafety}>
          <LifebuoyIcon width={20} height={20} aria-hidden='true' />
          <span>Need help now?</span>
        </SafetyButton>
      </DesktopNav>
    </>
  );
}

const MobileNav = styled.nav`
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 72px;
  background: ${({ theme }) => theme.colors.bg.elevated};
  border-top: 1px solid ${({ theme }) => theme.colors.border.subtle};
  display: flex;
  justify-content: space-around;
  padding: ${({ theme }) => theme.space[2]} ${({ theme }) => theme.space[2]}
    ${({ theme }) => theme.space[3]};
  z-index: 20;

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    display: none;
  }
`;

const DesktopNav = styled.nav`
  display: none;

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 240px;
    padding: ${({ theme }) => theme.space[6]};
    background: ${({ theme }) => theme.colors.bg.elevated};
    border-right: 1px solid ${({ theme }) => theme.colors.border.subtle};
    z-index: 10;
  }
`;

const Brand = styled.div`
  font-weight: ${({ theme }) => theme.typography.weights.semibold};
  color: ${({ theme }) => theme.colors.text.strong};
  letter-spacing: 0.02em;
  margin-bottom: ${({ theme }) => theme.space[6]};
`;

const Rail = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.space[2]};
  flex: 1;
`;

const linkBase = `
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0.75rem;
  border-radius: 0.75rem;
  text-decoration: none;
  color: inherit;
`;

const NavItem = styled(NavLink)`
  ${linkBase}
  flex: 1;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.4rem 0.25rem;
  border-radius: ${({ theme }) => theme.radii.md};
  color: ${({ theme }) => theme.colors.text.muted};
  font-size: ${({ theme }) => theme.typography.sizes.small};

  &.active {
    color: ${({ theme }) => theme.colors.primary.strong};
    background: ${({ theme }) => theme.colors.primary.soft};
  }
`;

const RailItem = styled(NavLink)`
  ${linkBase}
  color: ${({ theme }) => theme.colors.text.default};

  &.active {
    background: ${({ theme }) => theme.colors.primary.soft};
    border: 1px solid ${({ theme }) => theme.colors.primary.main};
  }
`;

const SafetyButton = styled.button`
  ${linkBase}
  border: 1px solid ${({ theme }) => theme.colors.border.subtle};
  background: ${({ theme }) => theme.colors.bg.soft};
  cursor: pointer;
`;
