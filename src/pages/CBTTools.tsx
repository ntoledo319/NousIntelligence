import { useState } from 'react';
import styled from 'styled-components';
import { useTherapeuticStore } from '../store/therapeuticStore';
import Button from '../components/Button/Button';
import { PlusIcon } from '@heroicons/react/24/outline';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const Header = styled.header`
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
`;

const Grid = styled.div`
  display: grid;
  gap: 1.5rem;
`;

const Card = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  padding: 1.5rem;
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  border: 1px solid ${({ theme }) => theme.colors.border};
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

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  font-family: inherit;
  font-size: 1rem;
  background: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.text};

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.primary}20;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  font-family: inherit;
  font-size: 1rem;
  min-height: 100px;
  resize: vertical;
  background: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.text};

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.primary}20;
  }
`;

const ThoughtCard = styled(Card)`
  margin-bottom: 1rem;
`;

const ThoughtHeader = styled.div`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: 0.5rem;
`;

const ThoughtText = styled.p`
  color: ${({ theme }) => theme.colors.textLight};
  margin: 0.5rem 0;
`;

const CBTTools: React.FC = () => {
  const { thoughtRecords, addThoughtRecord, isLoading } = useTherapeuticStore();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    situation: '',
    automaticThought: '',
    emotion: '',
    evidence: '',
    alternativeThought: '',
    outcome: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await addThoughtRecord({
      ...formData,
      evidence: formData.evidence.split('\n').filter(e => e.trim()),
    });
    setFormData({
      situation: '',
      automaticThought: '',
      emotion: '',
      evidence: '',
      alternativeThought: '',
      outcome: '',
    });
    setShowForm(false);
  };

  return (
    <Container>
      <Header>
        <Title>CBT Thought Records</Title>
        <Button
          variant="primary"
          icon={<PlusIcon />}
          onClick={() => setShowForm(!showForm)}
        >
          New Record
        </Button>
      </Header>

      {showForm && (
        <Card as="form" onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="situation">Situation</Label>
            <Input
              id="situation"
              value={formData.situation}
              onChange={(e) => setFormData({ ...formData, situation: e.target.value })}
              placeholder="What happened? Where were you?"
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="automaticThought">Automatic Thought</Label>
            <TextArea
              id="automaticThought"
              value={formData.automaticThought}
              onChange={(e) => setFormData({ ...formData, automaticThought: e.target.value })}
              placeholder="What went through your mind?"
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="emotion">Emotion</Label>
            <Input
              id="emotion"
              value={formData.emotion}
              onChange={(e) => setFormData({ ...formData, emotion: e.target.value })}
              placeholder="How did you feel?"
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="evidence">Evidence (one per line)</Label>
            <TextArea
              id="evidence"
              value={formData.evidence}
              onChange={(e) => setFormData({ ...formData, evidence: e.target.value })}
              placeholder="What supports this thought?\nWhat doesn't support it?"
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="alternativeThought">Alternative Thought</Label>
            <TextArea
              id="alternativeThought"
              value={formData.alternativeThought}
              onChange={(e) => setFormData({ ...formData, alternativeThought: e.target.value })}
              placeholder="What's a more balanced perspective?"
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="outcome">Outcome</Label>
            <Input
              id="outcome"
              value={formData.outcome}
              onChange={(e) => setFormData({ ...formData, outcome: e.target.value })}
              placeholder="How do you feel now?"
              required
            />
          </FormGroup>

          <Button type="submit" variant="primary" loading={isLoading}>
            Save Thought Record
          </Button>
        </Card>
      )}

      <Grid>
        {thoughtRecords.map((record) => (
          <ThoughtCard key={record.id}>
            <ThoughtHeader>Situation</ThoughtHeader>
            <ThoughtText>{record.situation}</ThoughtText>
            
            <ThoughtHeader>Automatic Thought</ThoughtHeader>
            <ThoughtText>{record.automaticThought}</ThoughtText>
            
            <ThoughtHeader>Emotion: {record.emotion}</ThoughtHeader>
            
            {record.evidence.length > 0 && (
              <>
                <ThoughtHeader>Evidence</ThoughtHeader>
                <ul>
                  {record.evidence.map((e, i) => (
                    <li key={i}><ThoughtText>{e}</ThoughtText></li>
                  ))}
                </ul>
              </>
            )}
            
            <ThoughtHeader>Alternative Thought</ThoughtHeader>
            <ThoughtText>{record.alternativeThought}</ThoughtText>
            
            <ThoughtHeader>Outcome</ThoughtHeader>
            <ThoughtText>{record.outcome}</ThoughtText>
          </ThoughtCard>
        ))}
      </Grid>
    </Container>
  );
};

export default CBTTools;
