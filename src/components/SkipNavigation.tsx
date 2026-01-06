import styled from 'styled-components';

const SkipLink = styled.a`
  position: absolute;
  top: -40px;
  left: 0;
  background: ${({ theme }) => theme.colors.primary};
  color: ${({ theme }) => theme.colors.textInverse};
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  border-radius: 0 0 ${({ theme }) => theme.radii.md} 0;
  font-weight: 600;
  z-index: 1000;
  transition: top ${({ theme }) => theme.transitions.fast};

  &:focus {
    top: 0;
    outline: 2px solid ${({ theme }) => theme.colors.textInverse};
    outline-offset: 2px;
  }
`;

export const SkipNavigation: React.FC = () => {
  return (
    <>
      <SkipLink href="#main-content">
        Skip to main content
      </SkipLink>
      <SkipLink href="#navigation" style={{ left: '150px' }}>
        Skip to navigation
      </SkipLink>
    </>
  );
};
