import { useState } from 'react';
import styled from 'styled-components';
import { useTherapeuticStore } from '../store/therapeuticStore';
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
  margin-bottom: 2rem;
`;

const MoodScale = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin: 2rem 0;
`;

const MoodButton = styled.button<{ $selected: boolean; $mood: number }>`
  flex: 1;
  padding: 1rem 0.5rem;
  border: 2px solid ${({ $selected, theme }) =>
    $selected ? theme.colors.primary : theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ $selected, $mood, theme }) => {
    if (!$selected) return theme.colors.surface;
    const hue = ($mood - 1) * 12;
    return `hsl(${hue}, 70%, 60%)`;
  }};
  color: ${({ $selected, theme }) =>
    $selected ? theme.colors.textInverse : theme.colors.text};
  font-weight: 600;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    transform: scale(1.05);
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
  margin-bottom: 1rem;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.primary}20;
  }
`;

const HistoryCard = styled(Card)`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
`;

const MoodValue = styled.div<{ $mood: number }>`
  font-size: 1.5rem;
  font-weight: 700;
  color: ${({ $mood }) => {
    const hue = ($mood - 1) * 12;
    return `hsl(${hue}, 70%, 50%)`;
  }};
`;

const MoodNote = styled.p`
  color: ${({ theme }) => theme.colors.textLight};
  flex: 1;
  margin: 0 1rem;
`;

const MoodDate = styled.time`
  color: ${({ theme }) => theme.colors.textLight};
  font-size: 0.875rem;
`;

const SubSectionTitle = styled.h2`
  margin-bottom: 1rem;
  color: ${({ theme }) => theme.colors.text};
  font-size: 1.5rem;
  font-weight: 600;
`;

const HelperText = styled.p`
  text-align: center;
  color: ${({ theme }) => theme.colors.textLight};
  margin-bottom: 1rem;
`;

const MoodTracker: React.FC = () => {
  const { moodHistory, addMoodEntry, isLoading } = useTherapeuticStore();
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [note, setNote] = useState('');

  const handleSubmit = async () => {
    if (selectedMood) {
      await addMoodEntry({ mood: selectedMood, note });
      setSelectedMood(null);
      setNote('');
    }
  };

  return (
    <Container>
      <Title>Mood Tracker</Title>
      
      <Card>
        <SubSectionTitle>How are you feeling?</SubSectionTitle>
        <MoodScale>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((mood) => (
            <MoodButton
              key={mood}
              $selected={selectedMood === mood}
              $mood={mood}
              onClick={() => setSelectedMood(mood)}
            >
              {mood}
            </MoodButton>
          ))}
        </MoodScale>
        <HelperText>
          1 = Very Low | 10 = Very High
        </HelperText>

        {selectedMood && (
          <>
            <TextArea
              placeholder="What's on your mind? (optional)"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
            <Button
              variant="primary"
              onClick={handleSubmit}
              loading={isLoading}
              disabled={!selectedMood}
            >
              Save Mood Entry
            </Button>
          </>
        )}
      </Card>

      <SubSectionTitle>Mood History</SubSectionTitle>
      {moodHistory.map((entry) => (
        <HistoryCard key={entry.id}>
          <MoodValue $mood={entry.mood}>{entry.mood}/10</MoodValue>
          <MoodNote>{entry.note || 'No notes'}</MoodNote>
          <MoodDate>
            {new Date(entry.timestamp).toLocaleDateString()}
          </MoodDate>
        </HistoryCard>
      ))}
    </Container>
  );
};

export default MoodTracker;
