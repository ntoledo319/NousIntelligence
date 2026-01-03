import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { useAuthStore } from '../store/authStore';
import { useTherapeuticStore } from '../store/therapeuticStore';
import { useChatStore } from '../store/chatStore';
import { Button } from '../components/Button/Button';
import {
  ChatBubbleLeftRightIcon,
  HeartIcon,
  ChartBarIcon,
  AcademicCapIcon,
} from '@heroicons/react/24/outline';

const DashboardContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const Header = styled.header`
  margin-bottom: 3rem;
`;

const Greeting = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text.primary};
  margin-bottom: 0.5rem;
`;

const Subheading = styled.p`
  font-size: 1.125rem;
  color: ${({ theme }) => theme.colors.text.secondary};
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;

  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }
`;

const Card = styled(Link)`
  background: ${({ theme }) => theme.colors.surface.default};
  padding: 2rem;
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.md};
  transition: all ${({ theme }) => theme.transitions.normal};
  border: 2px solid ${({ theme }) => theme.colors.border.default};
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: 1rem;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${({ theme }) => theme.shadows.lg};
    border-color: ${({ theme }) => theme.colors.primary.default};
  }
`;

const CardIcon = styled.div`
  width: 3rem;
  height: 3rem;
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.gradients.button};
  color: ${({ theme }) => theme.colors.text.inverse};
  display: flex;
  align-items: center;
  justify-content: center;

  svg {
    width: 1.75rem;
    height: 1.75rem;
  }
`;

const CardTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0;
`;

const CardDescription = styled.p`
  color: ${({ theme }) => theme.colors.text.secondary};
  line-height: 1.5;
  margin: 0;
`;

const StatsCard = styled.div`
  background: ${({ theme }) => theme.colors.surface.default};
  padding: 1.5rem;
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  border: 1px solid ${({ theme }) => theme.colors.border.default};
`;

const StatLabel = styled.div`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.text.secondary};
  margin-bottom: 0.5rem;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.primary.default};
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const { moodHistory, thoughtRecords, dbtSkills, loadData } = useTherapeuticStore();
  const { messages } = useChatStore();

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <DashboardContainer>
      <Header>
        <Greeting>Welcome back, {user?.name || 'Friend'}!</Greeting>
        <Subheading>Here's your wellness overview</Subheading>
      </Header>

      <StatsGrid>
        <StatsCard>
          <StatLabel>Chat Sessions</StatLabel>
          <StatValue>{messages.length}</StatValue>
        </StatsCard>
        <StatsCard>
          <StatLabel>Mood Entries</StatLabel>
          <StatValue>{moodHistory.length}</StatValue>
        </StatsCard>
        <StatsCard>
          <StatLabel>Thought Records</StatLabel>
          <StatValue>{thoughtRecords.length}</StatValue>
        </StatsCard>
        <StatsCard>
          <StatLabel>Skills Practiced</StatLabel>
          <StatValue>{dbtSkills.length}</StatValue>
        </StatsCard>
      </StatsGrid>

      <Grid>
        <Card to="/chat">
          <CardIcon>
            <ChatBubbleLeftRightIcon />
          </CardIcon>
          <CardTitle>AI Chat</CardTitle>
          <CardDescription>
            Start a conversation with your compassionate AI companion
          </CardDescription>
        </Card>

        <Card to="/cbt">
          <CardIcon>
            <AcademicCapIcon />
          </CardIcon>
          <CardTitle>CBT Tools</CardTitle>
          <CardDescription>
            Cognitive Behavioral Therapy exercises and thought records
          </CardDescription>
        </Card>

        <Card to="/dbt">
          <CardIcon>
            <HeartIcon />
          </CardIcon>
          <CardTitle>DBT Skills</CardTitle>
          <CardDescription>
            Dialectical Behavior Therapy techniques and skill logging
          </CardDescription>
        </Card>

        <Card to="/mood">
          <CardIcon>
            <ChartBarIcon />
          </CardIcon>
          <CardTitle>Mood Tracker</CardTitle>
          <CardDescription>
            Track and visualize your emotional patterns over time
          </CardDescription>
        </Card>

        <Card to="/crisis">
          <CardIcon>
            <HeartIcon />
          </CardIcon>
          <CardTitle>Crisis Support</CardTitle>
          <CardDescription>
            Immediate access to crisis resources and hotlines
          </CardDescription>
        </Card>

        <Card to="/settings">
          <CardIcon>
            <AcademicCapIcon />
          </CardIcon>
          <CardTitle>Settings</CardTitle>
          <CardDescription>
            Customize your experience and preferences
          </CardDescription>
        </Card>
      </Grid>
    </DashboardContainer>
  );
};

export default Dashboard;
