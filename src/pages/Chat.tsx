import { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';
import Button from '../components/Button/Button';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
`;

const ChatHeader = styled.header`
  background: ${({ theme }) => theme.colors.surface};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ChatTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
  margin: 0;
`;

const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const MessageBubble = styled.div<{ $isUser: boolean }>`
  align-self: ${({ $isUser }) => ($isUser ? 'flex-end' : 'flex-start')};
  max-width: 70%;
  padding: 0.875rem 1.25rem;
  border-radius: ${({ theme }) => theme.radii.lg};
  background: ${({ $isUser, theme }) =>
    $isUser ? theme.colors.primary : theme.colors.surface};
  color: ${({ $isUser, theme }) =>
    $isUser ? theme.colors.textInverse : theme.colors.text};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  word-wrap: break-word;
`;

const MessageText = styled.p`
  margin: 0;
  line-height: 1.5;
`;

const MessageTime = styled.time`
  display: block;
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.25rem;
`;

const InputArea = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  padding: 1rem 1.5rem;
  display: flex;
  gap: 0.75rem;
`;

const MessageInput = styled.textarea`
  flex: 1;
  padding: 0.875rem 1rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  font-family: inherit;
  font-size: 1rem;
  resize: none;
  min-height: 48px;
  max-height: 120px;
  background: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.text};

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.primary}20;
  }
`;

const EmotionIndicator = styled.div<{ $emotion?: string }>`
  padding: 0.5rem 1rem;
  background: ${({ theme }) => theme.colors.backgroundSoft};
  border-radius: ${({ theme }) => theme.radii.md};
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.textLight};
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Chat: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const { messages, isLoading, currentEmotion, addMessage, setLoading, setEmotion } = useChatStore();
  const { user } = useAuthStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    addMessage({ text: userMessage, sender: 'user' });
    setInputValue('');
    setLoading(true);

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          user_id: user?.id,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        addMessage({
          text: data.response || data.message || 'I understand.',
          sender: 'assistant',
          emotion: data.emotion,
          skillRecommendations: data.skill_recommendations,
        });

        if (data.emotion) {
          setEmotion(data.emotion);
        }
      } else {
        addMessage({
          text: 'I apologize, but I encountered an issue. Please try again.',
          sender: 'assistant',
        });
      }
    } catch (error) {
      console.error('Chat error:', error);
      addMessage({
        text: 'Connection error. Please check your internet connection and try again.',
        sender: 'assistant',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>🧠 NOUS Chat</ChatTitle>
        {currentEmotion && (
          <EmotionIndicator $emotion={currentEmotion}>
            Detected: {currentEmotion}
          </EmotionIndicator>
        )}
      </ChatHeader>

      <MessagesArea>
        {messages.map((message) => (
          <MessageBubble key={message.id} $isUser={message.sender === 'user'}>
            <MessageText>{message.text}</MessageText>
            <MessageTime>
              {new Date(message.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </MessageTime>
          </MessageBubble>
        ))}
        <div ref={messagesEndRef} />
      </MessagesArea>

      <InputArea>
        <MessageInput
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Share what's on your mind..."
          disabled={isLoading}
          aria-label="Chat message input"
        />
        <Button
          variant="primary"
          onClick={sendMessage}
          disabled={!inputValue.trim() || isLoading}
          loading={isLoading}
          icon={<PaperAirplaneIcon />}
          iconPosition="right"
          aria-label="Send message"
        >
          Send
        </Button>
      </InputArea>
    </ChatContainer>
  );
};

export default Chat;
