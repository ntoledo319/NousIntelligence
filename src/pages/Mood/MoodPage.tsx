/**
 * MoodPage (Mood Stream)
 *
 * Fast mood check-in connected to `/api/v2/mood/log`.
 *
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import styled from 'styled-components';

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
import { useExperienceMode } from '../../state/experienceMode';

type MoodItem = {
  mood: number;
  note?: string;
  tags?: string[];
  ts?: string;
};

type MoodRecentResponse = {
  ok: boolean;
  items: MoodItem[];
};

export function MoodPage() {
  const { mode } = useExperienceMode();
  const [mood, setMood] = React.useState<number>(6);
  const [tags, setTags] = React.useState<string[]>([]);
  const [note, setNote] = React.useState('');
  const [saving, setSaving] = React.useState(false);
  const [savedMsg, setSavedMsg] = React.useState<string | null>(null);
  const [recent, setRecent] = React.useState<MoodItem[]>([]);

  React.useEffect(() => {
    requestJson<MoodRecentResponse>('/api/v2/mood/recent?limit=10')
      .then((r) => setRecent(Array.isArray(r.items) ? r.items : []))
      .catch(() => setRecent([]));
  }, []);

  const toggleTag = (t: string) => {
    setTags((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]));
  };

  const submit = async () => {
    setSaving(true);
    setSavedMsg(null);
    try {
      await requestJson('/api/v2/mood/log', {
        method: 'POST',
        body: JSON.stringify({ mood, note, tags }),
      });
      setSavedMsg('Saved. Thank you for checking in.');
      setNote('');
      setTags([]);
      const r = await requestJson<MoodRecentResponse>('/api/v2/mood/recent?limit=10');
      setRecent(Array.isArray(r.items) ? r.items : []);
    } catch {
      setSavedMsg('Could not save right now. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const tagOptions = ['Sleep', 'Pain', 'Stress', 'People', 'Work', 'Money', 'Body'];

  return (
    <Page narrow>
      <Stack gap={6}>
        <SectionHeader
          title='Mood'
          description='A quick check-in. Optional context if you want it.'
        />

        <Surface>
          <Stack gap={4}>
            <Inline justify='space-between' align='center'>
              <strong>How are you doing, 1–10?</strong>
              <Pill aria-label={`Mood value ${mood} out of 10`}>{mood}/10</Pill>
            </Inline>

            <Range
              type='range'
              min={1}
              max={10}
              step={1}
              value={mood}
              onChange={(e) => setMood(Number(e.target.value))}
              aria-label='Mood rating from 1 to 10'
            />

            <Stack gap={2}>
              <strong>Context (optional)</strong>
              <Inline wrap gap={2}>
                {tagOptions.map((t) => (
                  <Chip key={t} selected={tags.includes(t)} onClick={() => toggleTag(t)}>
                    {t}
                  </Chip>
                ))}
              </Inline>
            </Stack>

            <Stack gap={2}>
              <strong>Anything you want to add?</strong>
              <TextArea
                placeholder='A sentence or two is enough.'
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
            </Stack>

            <PrimaryButton onClick={submit} isLoading={saving} fullWidth>
              Save check-in
            </PrimaryButton>

            {savedMsg ? <Small role='status'>{savedMsg}</Small> : null}
          </Stack>
        </Surface>

        {mode === 'structured' ? (
          <Surface>
            <Stack gap={3}>
              <strong>Recent check-ins</strong>
              {recent.length === 0 ? <Small>None yet.</Small> : null}
              {recent.slice(0, 5).map((i, idx) => (
                <Small key={`${i.ts ?? idx}`}>
                  {formatTs(i.ts)} · {Number(i.mood).toFixed(0)}/10
                  {Array.isArray(i.tags) && i.tags.length ? ` · ${i.tags.join(', ')}` : ''}
                </Small>
              ))}
            </Stack>
          </Surface>
        ) : null}
      </Stack>
    </Page>
  );
}

function formatTs(ts?: string) {
  if (!ts) return '';
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric' });
}

const Range = styled.input`
  width: 100%;
  accent-color: ${({ theme }) => theme.colors.primary.main};
`;

const Pill = styled.div`
  background: ${({ theme }) => theme.colors.primary.soft};
  color: ${({ theme }) => theme.colors.primary.strong};
  border-radius: ${({ theme }) => theme.radii.pill};
  padding: ${({ theme }) => theme.space[1]} ${({ theme }) => theme.space[3]};
  font-size: ${({ theme }) => theme.typography.sizes.small};
`;

const Small = styled.div`
  color: ${({ theme }) => theme.colors.text.muted};
  font-size: ${({ theme }) => theme.typography.sizes.small};
`;
