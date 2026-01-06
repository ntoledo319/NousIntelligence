import { useState } from 'react';
import styled from 'styled-components';
import { useTherapeuticStore } from '../store/therapeuticStore';
import Button from '../components/Button/Button';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: 2rem;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
`;

const SkillCard = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  padding: 1.5rem;
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  border: 2px solid ${({ theme }) => theme.colors.border};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.normal};

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${({ theme }) => theme.shadows.md};
    border-color: ${({ theme }) => theme.colors.primary};
  }
`;

const SkillTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: ${({ theme }) => theme.colors.text};
`;

const SkillDescription = styled.p`
  color: ${({ theme }) => theme.colors.textLight};
  margin-bottom: 1rem;
  line-height: 1.5;
`;

const Category = styled.span`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: ${({ theme }) => theme.colors.primary}20;
  color: ${({ theme }) => theme.colors.primary};
  border-radius: ${({ theme }) => theme.radii.sm};
  font-size: 0.875rem;
  font-weight: 600;
`;

const DBT_SKILLS = [
  {
    name: 'TIPP',
    category: 'Distress Tolerance',
    description: 'Temperature, Intense exercise, Paced breathing, Paired muscle relaxation - for crisis moments',
  },
  {
    name: 'Radical Acceptance',
    category: 'Distress Tolerance',
    description: 'Accepting reality as it is, without judgment or resistance',
  },
  {
    name: 'Mindfulness',
    category: 'Core Mindfulness',
    description: 'Being present in the moment with awareness and without judgment',
  },
  {
    name: 'Wise Mind',
    category: 'Core Mindfulness',
    description: 'Balance between emotion mind and reasonable mind',
  },
  {
    name: 'Opposite Action',
    category: 'Emotion Regulation',
    description: 'Acting opposite to harmful emotional urges',
  },
  {
    name: 'PLEASE',
    category: 'Emotion Regulation',
    description: 'PhysicaL illness, Eating, Avoid mood-altering substances, Sleep, Exercise',
  },
  {
    name: 'DEAR MAN',
    category: 'Interpersonal Effectiveness',
    description: 'Describe, Express, Assert, Reinforce, Mindful, Appear confident, Negotiate',
  },
  {
    name: 'STOP Skill',
    category: 'Distress Tolerance',
    description: 'Stop, Take a step back, Observe, Proceed mindfully',
  },
];

const DBTSkills: React.FC = () => {
  const { logDBTSkill, isLoading } = useTherapeuticStore();
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);

  const handleSkillClick = async (skill: typeof DBT_SKILLS[0]) => {
    setSelectedSkill(skill.name);
    await logDBTSkill({
      name: skill.name,
      category: skill.category,
      description: skill.description,
    });
    setTimeout(() => setSelectedSkill(null), 1500);
  };

  return (
    <Container>
      <Title>DBT Skills Library</Title>
      <Grid>
        {DBT_SKILLS.map((skill) => (
          <SkillCard
            key={skill.name}
            onClick={() => handleSkillClick(skill)}
            style={{
              opacity: isLoading && selectedSkill === skill.name ? 0.6 : 1,
            }}
          >
            <SkillTitle>{skill.name}</SkillTitle>
            <SkillDescription>{skill.description}</SkillDescription>
            <Category>{skill.category}</Category>
          </SkillCard>
        ))}
      </Grid>
    </Container>
  );
};

export default DBTSkills;
