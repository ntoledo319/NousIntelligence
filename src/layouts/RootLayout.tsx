import { Outlet } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import styled from 'styled-components';

const LayoutContainer = styled.div`
  min-height: 100vh;
  background-color: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.text};
  font-family: ${({ theme }) => theme.fonts.body};
`;

export const RootLayout: React.FC = () => {
  const checkAuth = useAuthStore((state) => state.checkAuth);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <LayoutContainer>
      <Outlet />
    </LayoutContainer>
  );
};
