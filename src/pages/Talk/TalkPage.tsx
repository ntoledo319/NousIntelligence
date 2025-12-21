/**
 * TalkPage (AI chat)
 *
 * Calm chat interface using `/api/v1/chat`.
 *
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import styled, { type DefaultTheme } from 'styled-components';

import {
  Chip,
  Inline,
  Page,
  PrimaryButton,
  SectionHeader,
  Stack,
  Surface,
  TextArea,
} from '../../components/ui';
import { requestJson } from '../../services/apiClient';

type ChatMessage = {
  id: string;
  role: 'system' | 'user' | 'assistant';
  text: string;
};

export function TalkPage() {
  const [messages, setMessages] = React.useState<ChatMessage[]>([
    {
      id: 'sys',
      role: 'system',
      text: 'I’m here with you. I’m not a therapist, but I can help you slow down and find a next step.',
    },
  ]);
  const [input, setInput] = React.useState('');
  const [sending, setSending] = React.useState(false);

  const starters = [
    'Help me untangle today',
    'I’m spiraling about something',
    'I just need someone to sit with me',
  ];

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    setInput('');
    setSending(true);
    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: 'user', text: trimmed };
    setMessages((m) => [...m, userMsg]);

    // Gentle local safety nudge (no red alarms).
    const risk = /(suicide|kill myself|end it|self-harm|hurt myself)/i.test(trimmed);
    if (risk) {
      setMessages((m) => [
        ...m,
        {
          id: `safety-${Date.now()}`,
          role: 'system',
          text: 'If you might be in danger, you deserve immediate support. You can open “Need help now?” at any time.',
        },
      ]);
    }

    try {
      const r = await requestJson<{ response: string }>('/api/v1/chat', {
        method: 'POST',
        body: JSON.stringify({ message: trimmed }),
      });
      setMessages((m) => [...m, { id: `a-${Date.now()}`, role: 'assistant', text: r.response }]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: `a-${Date.now()}`,
          role: 'assistant',
          text: 'I couldn’t send that right now. Want to try again?',
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <Page>
      <Stack gap={6}>
        <SectionHeader
          title='Talk'
          description='A calm place to untangle what’s happening, at your pace.'
        />

        <Surface>
          <Stack gap={4}>
            <Inline wrap gap={2}>
              {starters.map((s) => (
                <Chip key={s} onClick={() => send(s)}>
                  {s}
                </Chip>
              ))}
            </Inline>

            <ChatLog aria-label='Conversation'>
              {messages.map((m) => (
                <Bubble key={m.id} $role={m.role}>
                  {m.text}
                </Bubble>
              ))}
              {sending ? <Bubble $role='system'>Sending…</Bubble> : null}
            </ChatLog>

            <Stack gap={2}>
              <TextArea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder='Type a message…'
                aria-label='Message'
              />
              <PrimaryButton
                onClick={() => send(input)}
                disabled={!input.trim()}
                isLoading={sending}
                fullWidth
              >
                Send
              </PrimaryButton>
            </Stack>
          </Stack>
        </Surface>
      </Stack>
    </Page>
  );
}

const ChatLog = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.space[3]};
`;

const Bubble = styled.div<{ $role: ChatMessage['role'] }>`
  max-width: 72ch;
  padding: ${({ theme }) => theme.space[3]} ${({ theme }) => theme.space[4]};
  border-radius: ${({ theme }) => theme.radii.lg};
  border: 1px solid ${({ theme }) => theme.colors.border.subtle};
  background: ${({ theme, $role }) => bubbleBackground(theme, $role)};
  align-self: ${({ $role }) => ($role === 'user' ? 'flex-end' : 'flex-start')};
`;

function bubbleBackground(theme: DefaultTheme, role: ChatMessage['role']) {
  if (role === 'user') return theme.colors.primary.soft;
  if (role === 'system') return theme.colors.bg.soft;
  return theme.colors.bg.elevated;
}
