import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/Button/Button';
import { SparklesIcon, HeartIcon, AcademicCapIcon, ChartBarIcon } from '@heroicons/react/24/outline';

const LandingContainer = styled.div`
  min-height: 100vh;
  background: ${({ theme }) => theme.gradients.hero};
`;

const HeroSection = styled.section`
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
    animation: shimmer 3s ease-in-out infinite;
    pointer-events: none;
  }

  @keyframes shimmer {
    0%, 100% { transform: translateX(-100%); opacity: 0; }
    50% { transform: translateX(100%); opacity: 1; }
  }
`;

const HeroContent = styled.div`
  max-width: 42rem;
  position: relative;
  z-index: 1;
`;

const Logo = styled.div`
  font-size: 4.5rem;
  margin-bottom: 1.5rem;
  animation: float 3s ease-in-out infinite;

  @keyframes float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    33% { transform: translateY(-8px) rotate(2deg); }
    66% { transform: translateY(-4px) rotate(-1deg); }
  }
`;

const Title = styled.h1`
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  color: ${({ theme }) => theme.colors.text.inverse};
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);

  @media (min-width: 768px) {
    font-size: 4rem;
  }
`;

const Subtitle = styled.p`
  font-size: 1.5rem;
  font-weight: 400;
  margin-bottom: 2rem;
  color: ${({ theme }) => theme.colors.text.inverse};
  opacity: 0.95;

  @media (min-width: 768px) {
    font-size: 1.75rem;
  }
`;

const Description = styled.p`
  font-size: 1.125rem;
  line-height: 1.7;
  opacity: 0.9;
  margin-bottom: 2.5rem;
  color: ${({ theme }) => theme.colors.text.inverse};
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;

  @media (min-width: 768px) {
    flex-direction: row;
    justify-content: center;
    gap: 1.5rem;
  }
`;

const FeaturesSection = styled.section`
  padding: 4rem 2rem;
  background: ${({ theme }) => theme.colors.background.default};
`;

const FeaturesGrid = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;

  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(4, 1fr);
  }
`;

const FeatureCard = styled.div`
  background: ${({ theme }) => theme.gradients.card};
  padding: 2rem;
  border-radius: ${({ theme }) => theme.radii.lg};
  text-align: center;
  box-shadow: ${({ theme }) => theme.shadows.md};
  transition: all ${({ theme }) => theme.transitions.normal};
  border: 2px solid transparent;

  &:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: ${({ theme }) => theme.shadows.lg};
    border-color: ${({ theme }) => theme.colors.primary.light};
  }
`;

const FeatureIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
  color: ${({ theme }) => theme.colors.primary.default};
  
  svg {
    width: 3rem;
    height: 3rem;
  }
`;

const FeatureTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: ${({ theme }) => theme.colors.text.primary};
`;

const FeatureDescription = styled.p`
  color: ${({ theme }) => theme.colors.text.secondary};
  line-height: 1.6;
`;

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      window.location.href = '/auth/google';
    }
  };

  const handleDemo = () => {
    window.location.href = '/chat/demo';
  };

  return (
    <LandingContainer>
      <HeroSection>
        <HeroContent>
          <Logo>🧠</Logo>
          <Title>NOUS Intelligence</Title>
          <Subtitle>Your Compassionate AI Companion</Subtitle>
          <Description>
            Experience personalized mental wellness support powered by advanced AI.
            CBT, DBT, and evidence-based therapeutic tools at your fingertips.
          </Description>
          <ButtonGroup>
            <Button
              variant="primary"
              size="large"
              onClick={handleGetStarted}
            >
              Get Started
            </Button>
            <Button
              variant="secondary"
              size="large"
              onClick={handleDemo}
            >
              Try Demo
            </Button>
          </ButtonGroup>
        </HeroContent>
      </HeroSection>

      <FeaturesSection>
        <FeaturesGrid>
          <FeatureCard>
            <FeatureIcon>
              <SparklesIcon />
            </FeatureIcon>
            <FeatureTitle>AI-Powered Support</FeatureTitle>
            <FeatureDescription>
              Emotion-aware conversations that adapt to your unique needs
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>
              <AcademicCapIcon />
            </FeatureIcon>
            <FeatureTitle>CBT & DBT Tools</FeatureTitle>
            <FeatureDescription>
              Evidence-based therapeutic techniques for lasting change
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>
              <ChartBarIcon />
            </FeatureIcon>
            <FeatureTitle>Mood Tracking</FeatureTitle>
            <FeatureDescription>
              Visualize patterns and gain insights into your well-being
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>
              <HeartIcon />
            </FeatureIcon>
            <FeatureTitle>Crisis Support</FeatureTitle>
            <FeatureDescription>
              24/7 access to resources when you need them most
            </FeatureDescription>
          </FeatureCard>
        </FeaturesGrid>
      </FeaturesSection>
    </LandingContainer>
  );
};

export default Landing;
