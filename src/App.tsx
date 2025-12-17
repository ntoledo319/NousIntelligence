import React from 'react';
import { ThemeProvider } from 'styled-components';
import { theme } from './theme';
import Button from './components/Button';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <div style={{
        padding: '2rem',
        fontFamily: theme.fonts.body,
        minHeight: '100vh',
        backgroundColor: '#f9fafb'
      }}>
        <header style={{ marginBottom: '2rem' }}>
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: 'bold',
            color: theme.colors.primary,
            marginBottom: '0.5rem'
          }}>
            Nous Intelligence
          </h1>
          <p style={{
            fontSize: '1.125rem',
            color: theme.colors.textLight
          }}>
            AI-Powered Intelligence Platform
          </p>
        </header>

        <main>
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '0.5rem',
            boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
            maxWidth: '800px'
          }}>
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: '600',
              marginBottom: '1rem',
              color: theme.colors.text
            }}>
              Welcome to Nous Intelligence
            </h2>
            <p style={{
              color: theme.colors.textLight,
              marginBottom: '1.5rem'
            }}>
              The UI frontend is now operational. This is a basic starter interface.
            </p>

            <div style={{
              display: 'flex',
              gap: '1rem',
              flexWrap: 'wrap',
              marginBottom: '1.5rem'
            }}>
              <Button variant="primary">
                Primary Button
              </Button>
              <Button variant="secondary">
                Secondary Button
              </Button>
              <Button variant="danger">
                Danger Button
              </Button>
              <Button variant="outline">
                Outline Button
              </Button>
              <Button variant="ghost">
                Ghost Button
              </Button>
            </div>

            <div style={{
              display: 'flex',
              gap: '1rem',
              flexWrap: 'wrap',
              marginBottom: '1.5rem'
            }}>
              <Button size="small">Small</Button>
              <Button size="medium">Medium</Button>
              <Button size="large">Large</Button>
            </div>

            <div style={{
              display: 'flex',
              gap: '1rem',
              flexWrap: 'wrap'
            }}>
              <Button isLoading>Loading...</Button>
              <Button disabled disabledTooltip="This button is disabled">
                Disabled
              </Button>
            </div>
          </div>
        </main>
      </div>
    </ThemeProvider>
  );
};

export default App;
