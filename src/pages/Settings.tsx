import { useState } from 'react';
import styled from 'styled-components';
import { useAuthStore } from '../store/authStore';
import Button from '../components/Button/Button';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: 2rem;
`;

const Card = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  padding: 2rem;
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  border: 1px solid ${({ theme }) => theme.colors.border};
  margin-bottom: 1.5rem;
`;

const SectionTitle = styled.h2`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: 1rem;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: ${({ theme }) => theme.colors.text};
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  font-family: inherit;
  font-size: 1rem;
  background: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.text};
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.primary}20;
  }
`;

const Checkbox = styled.input`
  margin-right: 0.75rem;
  cursor: pointer;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  cursor: pointer;
  color: ${({ theme }) => theme.colors.text};
`;

const HelperText = styled.p`
  margin-bottom: 1rem;
  color: ${({ theme }) => theme.colors.textLight};
`;

const Settings: React.FC = () => {
  const { user, updatePreferences, logout } = useAuthStore();
  const [theme, setTheme] = useState(user?.preferences?.theme || 'limen-harbor');
  const [locale, setLocale] = useState(user?.preferences?.locale || 'en');
  const [notifications, setNotifications] = useState(user?.preferences?.notifications ?? true);

  const handleSave = () => {
    updatePreferences({ theme, locale, notifications });
    alert('Settings saved successfully!');
  };

  return (
    <Container>
      <Title>Settings</Title>

      <Card>
        <SectionTitle>Appearance</SectionTitle>
        <FormGroup>
          <Label htmlFor="theme">Theme</Label>
          <Select
            id="theme"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
          >
            <option value="limen-harbor">Limen Harbor (Default)</option>
            <option value="limen-harbor-dark">Limen Harbor Dark</option>
            <option value="ocean">Ocean</option>
            <option value="forest">Forest</option>
            <option value="sunset">Sunset</option>
            <option value="purple">Purple</option>
            <option value="pink">Pink</option>
          </Select>
        </FormGroup>
      </Card>

      <Card>
        <SectionTitle>Language & Region</SectionTitle>
        <FormGroup>
          <Label htmlFor="locale">Language</Label>
          <Select
            id="locale"
            value={locale}
            onChange={(e) => setLocale(e.target.value)}
          >
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
          </Select>
        </FormGroup>
      </Card>

      <Card>
        <SectionTitle>Notifications</SectionTitle>
        <CheckboxLabel>
          <Checkbox
            type="checkbox"
            checked={notifications}
            onChange={(e) => setNotifications(e.target.checked)}
          />
          Enable notifications for reminders and updates
        </CheckboxLabel>
      </Card>

      <Card>
        <SectionTitle>Account</SectionTitle>
        <HelperText>
          Signed in as: {user?.email || user?.name || 'Guest'}
        </HelperText>
        <Button variant="danger" onClick={logout}>
          Sign Out
        </Button>
      </Card>

      <Button variant="primary" onClick={handleSave}>
        Save Settings
      </Button>
    </Container>
  );
};

export default Settings;
