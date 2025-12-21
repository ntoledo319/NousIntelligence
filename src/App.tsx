/**
 * App root (Lumen Harbor SPA).
 *
 * This file will become the Lumen Harbor app shell (routing + navigation).
 * Hosts the router and app shell.
 *
 * # AI-GENERATED 2025-12-21
 */
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';

import { AppShell } from './layout/AppShell';
import { HarborHomePage } from './pages/HarborHome/HarborHomePage';
import { JournalPage } from './pages/Journal/JournalPage';
import { MoodPage } from './pages/Mood/MoodPage';
import { MorePage } from './pages/More/MorePage';
import { TalkPage } from './pages/Talk/TalkPage';
import { ExperienceModeProvider } from './state/experienceMode';
import { GlobalStyle } from './styles/GlobalStyle';
import { theme } from './theme';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <ExperienceModeProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<AppShell />}>
              <Route path='/' element={<HarborHomePage />} />
              <Route path='/mood' element={<MoodPage />} />
              <Route path='/journal' element={<JournalPage />} />
              <Route path='/talk' element={<TalkPage />} />
              <Route path='/more' element={<MorePage />} />
              <Route path='*' element={<Navigate to='/' replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ExperienceModeProvider>
    </ThemeProvider>
  );
};

export default App;
