import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuthStore } from '../../store/authStore';
import Button from '../Button/Button';
import { ArrowRightIcon, CheckIcon } from '@heroicons/react/24/outline';

const Container = styled.div`
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

const ProgressBar = styled.div`
  height: 4px;
  background: ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.full};
  margin-bottom: 2rem;
  overflow: hidden;
`;

const Progress = styled.div<{ $progress: number }>`
  height: 100%;
  width: ${({ $progress }) => $progress}%;
  background: ${({ theme }) => theme.gradients.button};
  transition: width 0.3s ease;
`;

const Card = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  padding: 2.5rem;
  border-radius: ${({ theme }) => theme.radii.xl};
  box-shadow: ${({ theme }) => theme.shadows.lg};
`;

const Title = styled.h2`
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: ${({ theme }) => theme.colors.text};
`;

const Description = styled.p`
  color: ${({ theme }) => theme.colors.textLight};
  line-height: 1.6;
  margin-bottom: 2rem;
`;

const OptionGrid = styled.div`
  display: grid;
  gap: 1rem;
  margin-bottom: 2rem;
`;

const OptionButton = styled.button<{ $selected: boolean }>`
  padding: 1.25rem;
  border: 2px solid ${({ $selected, theme }) =>
    $selected ? theme.colors.primary : theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.lg};
  background: ${({ $selected, theme }) =>
    $selected ? theme.colors.primary + '1a' : theme.colors.background};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.normal};
  text-align: left;
  display: flex;
  align-items: center;
  gap: 1rem;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    transform: translateY(-2px);
  }
`;

const OptionTitle = styled.div`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const OptionDescription = styled.div`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.textLight};
  margin-top: 0.25rem;
`;

const CheckMark = styled.div<{ $visible: boolean }>`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: ${({ $visible }) => ($visible ? 1 : 0)};
  transition: opacity ${({ theme }) => theme.transitions.fast};

  svg {
    width: 16px;
    height: 16px;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
`;

const STEPS = [
  {
    id: 'welcome',
    title: 'Welcome to NOUS',
    description: 'Let\'s personalize your experience. This will only take a minute.',
    type: 'info',
  },
  {
    id: 'goals',
    title: 'What brings you here today?',
    description: 'Select all that apply. You can change these later.',
    type: 'multi-select',
    options: [
      { id: 'anxiety', label: 'Managing Anxiety', description: 'Reduce worry and find calm' },
      { id: 'mood', label: 'Mood Tracking', description: 'Understand emotional patterns' },
      { id: 'cbt', label: 'CBT Tools', description: 'Challenge negative thoughts' },
      { id: 'dbt', label: 'DBT Skills', description: 'Build distress tolerance' },
      { id: 'support', label: 'General Support', description: 'Compassionate conversation' },
    ],
  },
  {
    id: 'notifications',
    title: 'Stay on track with reminders',
    description: 'Would you like gentle reminders to check in with yourself?',
    type: 'single-select',
    options: [
      { id: 'daily', label: 'Daily reminders', description: 'One gentle nudge each day' },
      { id: 'custom', label: 'Custom schedule', description: 'Choose your own times' },
      { id: 'none', label: 'No reminders', description: 'I\'ll check in on my own' },
    ],
  },
  {
    id: 'complete',
    title: 'You\'re all set!',
    description: 'Your personalized wellness journey starts now. We\'re here whenever you need us.',
    type: 'info',
  },
];

export const OnboardingFlow: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selections, setSelections] = useState<Record<string, string[]>>({});
  const navigate = useNavigate();
  const { updatePreferences } = useAuthStore();

  const step = STEPS[currentStep];
  const progress = ((currentStep + 1) / STEPS.length) * 100;

  const handleSelect = (optionId: string) => {
    const stepId = step.id;
    if (step.type === 'multi-select') {
      setSelections((prev) => ({
        ...prev,
        [stepId]: prev[stepId]?.includes(optionId)
          ? prev[stepId].filter((id) => id !== optionId)
          : [...(prev[stepId] || []), optionId],
      }));
    } else if (step.type === 'single-select') {
      setSelections((prev) => ({
        ...prev,
        [stepId]: [optionId],
      }));
    }
  };

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Save preferences
      updatePreferences({
        onboardingComplete: true,
        goals: selections.goals || [],
        notificationPreference: selections.notifications?.[0] || 'none',
      });
      navigate('/dashboard');
    }
  };

  const handleSkip = () => {
    updatePreferences({ onboardingComplete: true });
    navigate('/dashboard');
  };

  const canProceed =
    step.type === 'info' ||
    (selections[step.id] && selections[step.id].length > 0);

  return (
    <Container>
      <ProgressBar>
        <Progress $progress={progress} />
      </ProgressBar>

      <Card>
        <Title>{step.title}</Title>
        <Description>{step.description}</Description>

        {step.type === 'multi-select' && (
          <OptionGrid>
            {step.options?.map((option) => (
              <OptionButton
                key={option.id}
                $selected={selections[step.id]?.includes(option.id) || false}
                onClick={() => handleSelect(option.id)}
              >
                <div style={{ flex: 1 }}>
                  <OptionTitle>{option.label}</OptionTitle>
                  <OptionDescription>{option.description}</OptionDescription>
                </div>
                <CheckMark $visible={selections[step.id]?.includes(option.id) || false}>
                  <CheckIcon />
                </CheckMark>
              </OptionButton>
            ))}
          </OptionGrid>
        )}

        {step.type === 'single-select' && (
          <OptionGrid>
            {step.options?.map((option) => (
              <OptionButton
                key={option.id}
                $selected={selections[step.id]?.includes(option.id) || false}
                onClick={() => handleSelect(option.id)}
              >
                <div style={{ flex: 1 }}>
                  <OptionTitle>{option.label}</OptionTitle>
                  <OptionDescription>{option.description}</OptionDescription>
                </div>
                <CheckMark $visible={selections[step.id]?.includes(option.id) || false}>
                  <CheckIcon />
                </CheckMark>
              </OptionButton>
            ))}
          </OptionGrid>
        )}

        <ButtonGroup>
          {currentStep > 0 && currentStep < STEPS.length - 1 && (
            <Button variant="ghost" onClick={handleSkip}>
              Skip
            </Button>
          )}
          <Button
            variant="primary"
            onClick={handleNext}
            disabled={!canProceed}
            icon={currentStep < STEPS.length - 1 ? <ArrowRightIcon /> : undefined}
            iconPosition="right"
          >
            {currentStep < STEPS.length - 1 ? 'Continue' : 'Get Started'}
          </Button>
        </ButtonGroup>
      </Card>
    </Container>
  );
};
