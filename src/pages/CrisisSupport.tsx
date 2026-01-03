import styled from 'styled-components';
import { PhoneIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
`;

const Alert = styled.div`
  background: ${({ theme }) => theme.colors.error.bg};
  border: 2px solid ${({ theme }) => theme.colors.error.default};
  border-radius: ${({ theme }) => theme.radii.lg};
  padding: 1.5rem;
  margin-bottom: 2rem;
`;

const AlertTitle = styled.h2`
  color: ${({ theme }) => theme.colors.error.default};
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
`;

const AlertText = styled.p`
  color: ${({ theme }) => theme.colors.text.primary};
  line-height: 1.6;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text.primary};
  margin-bottom: 1.5rem;
`;

const ResourceCard = styled.a`
  display: block;
  background: ${({ theme }) => theme.colors.surface.default};
  padding: 1.5rem;
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  border: 2px solid ${({ theme }) => theme.colors.border.default};
  margin-bottom: 1rem;
  text-decoration: none;
  transition: all ${({ theme }) => theme.transitions.normal};

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${({ theme }) => theme.shadows.md};
    border-color: ${({ theme }) => theme.colors.primary.default};
  }
`;

const ResourceHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
`;

const ResourceIcon = styled.div`
  width: 3rem;
  height: 3rem;
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.primary.default};
  color: ${({ theme }) => theme.colors.text.inverse};
  display: flex;
  align-items: center;
  justify-content: center;

  svg {
    width: 1.5rem;
    height: 1.5rem;
  }
`;

const ResourceTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0;
`;

const ResourceDescription = styled.p`
  color: ${({ theme }) => theme.colors.text.secondary};
  line-height: 1.5;
  margin: 0;
`;

const PhoneNumber = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.primary.default};
  margin-top: 0.5rem;
`;

const CrisisSupport: React.FC = () => {
  return (
    <Container>
      <Alert>
        <AlertTitle>🚨 If you're in immediate danger</AlertTitle>
        <AlertText>
          Please call 911 or go to your nearest emergency room. Your safety is the top priority.
        </AlertText>
      </Alert>

      <Title>Crisis Support Resources</Title>

      <ResourceCard href="tel:988">
        <ResourceHeader>
          <ResourceIcon>
            <PhoneIcon />
          </ResourceIcon>
          <ResourceTitle>988 Suicide & Crisis Lifeline</ResourceTitle>
        </ResourceHeader>
        <ResourceDescription>
          Free and confidential support for people in distress, 24/7
        </ResourceDescription>
        <PhoneNumber>Call or text 988</PhoneNumber>
      </ResourceCard>

      <ResourceCard href="tel:1-800-273-8255">
        <ResourceHeader>
          <ResourceIcon>
            <PhoneIcon />
          </ResourceIcon>
          <ResourceTitle>National Suicide Prevention Lifeline</ResourceTitle>
        </ResourceHeader>
        <ResourceDescription>
          24/7 free and confidential support
        </ResourceDescription>
        <PhoneNumber>1-800-273-8255</PhoneNumber>
      </ResourceCard>

      <ResourceCard href="sms:741741">
        <ResourceHeader>
          <ResourceIcon>
            <ChatBubbleLeftRightIcon />
          </ResourceIcon>
          <ResourceTitle>Crisis Text Line</ResourceTitle>
        </ResourceHeader>
        <ResourceDescription>
          Text with a trained crisis counselor, 24/7
        </ResourceDescription>
        <PhoneNumber>Text HOME to 741741</PhoneNumber>
      </ResourceCard>

      <ResourceCard href="tel:1-866-488-7386">
        <ResourceHeader>
          <ResourceIcon>
            <PhoneIcon />
          </ResourceIcon>
          <ResourceTitle>Trevor Project (LGBTQ+ Youth)</ResourceTitle>
        </ResourceHeader>
        <ResourceDescription>
          Crisis intervention and suicide prevention for LGBTQ+ young people
        </ResourceDescription>
        <PhoneNumber>1-866-488-7386</PhoneNumber>
      </ResourceCard>

      <ResourceCard href="tel:1-877-565-8860">
        <ResourceHeader>
          <ResourceIcon>
            <PhoneIcon />
          </ResourceIcon>
          <ResourceTitle>Trans Lifeline</ResourceTitle>
        </ResourceHeader>
        <ResourceDescription>
          Support hotline run by and for transgender people
        </ResourceDescription>
        <PhoneNumber>1-877-565-8860</PhoneNumber>
      </ResourceCard>

      <ResourceCard href="tel:1-800-799-7233">
        <ResourceHeader>
          <ResourceIcon>
            <PhoneIcon />
          </ResourceIcon>
          <ResourceTitle>National Domestic Violence Hotline</ResourceTitle>
        </ResourceHeader>
        <ResourceDescription>
          Confidential support for domestic violence survivors
        </ResourceDescription>
        <PhoneNumber>1-800-799-7233</PhoneNumber>
      </ResourceCard>
    </Container>
  );
};

export default CrisisSupport;
