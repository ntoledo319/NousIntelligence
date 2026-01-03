import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { RootLayout } from '../layouts/RootLayout';

const Landing = lazy(() => import('../pages/Landing'));
const Chat = lazy(() => import('../pages/Chat'));
const CBTTools = lazy(() => import('../pages/CBTTools'));
const DBTSkills = lazy(() => import('../pages/DBTSkills'));
const MoodTracker = lazy(() => import('../pages/MoodTracker'));
const Dashboard = lazy(() => import('../pages/Dashboard'));
const Settings = lazy(() => import('../pages/Settings'));
const CrisisSupport = lazy(() => import('../pages/CrisisSupport'));

const withSuspense = (Component: React.ComponentType) => (
  <Suspense fallback={<LoadingSpinner />}>
    <Component />
  </Suspense>
);

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: withSuspense(Landing),
      },
      {
        path: 'chat',
        element: (
          <ProtectedRoute>
            {withSuspense(Chat)}
          </ProtectedRoute>
        ),
      },
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute>
            {withSuspense(Dashboard)}
          </ProtectedRoute>
        ),
      },
      {
        path: 'cbt',
        element: (
          <ProtectedRoute>
            {withSuspense(CBTTools)}
          </ProtectedRoute>
        ),
      },
      {
        path: 'dbt',
        element: (
          <ProtectedRoute>
            {withSuspense(DBTSkills)}
          </ProtectedRoute>
        ),
      },
      {
        path: 'mood',
        element: (
          <ProtectedRoute>
            {withSuspense(MoodTracker)}
          </ProtectedRoute>
        ),
      },
      {
        path: 'crisis',
        element: withSuspense(CrisisSupport),
      },
      {
        path: 'settings',
        element: (
          <ProtectedRoute>
            {withSuspense(Settings)}
          </ProtectedRoute>
        ),
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
