/**
 * HarborHomePage
 *
 * Purpose:
 * - Orient without overwhelm
 * - Offer low-effort, autonomy-supportive next steps
 *
 * Backend:
 * - Mood mini-summary uses `GET /api/v2/mood/recent?limit=7`
 *
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import { Link } from 'react-router-dom';
import styled from 'styled-components';

import { Page, SectionHeader, Stack, Surface, Inline, GhostButton } from '../../components/ui';
import { useLocalStorageState } from '../../hooks/useLocalStorageState';
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

export function HarborHomePage() {
  const { mode } = useExperienceMode();
  const [dismissed, setDismissed] = useLocalStorageState<boolean>(
    'lumen.onboardingDismissed',
    false
  );
  const [items, setItems] = React.useState<MoodItem[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;
    setLoading(true);
    requestJson<MoodRecentResponse>('/api/v2/mood/recent?limit=7')
      .then((r) => {
        if (cancelled) return;
        setItems(Array.isArray(r.items) ? r.items : []);
      })
      .catch(() => {
        if (cancelled) return;
        setItems([]);
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const dateLabel = new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  });

  const last7 = toChronological(items).slice(-7);
  const avg =
    last7.length > 0
      ? last7.reduce((acc, i) => acc + (Number(i.mood) || 0), 0) / last7.length
      : null;

  return (
    <Page>
      <Stack gap={6}>
        <Stack gap={2}>
          <Meta>{dateLabel}</Meta>
          <SectionHeader
            title='How’s the weather inside today?'
            description='A quiet place to land. Choose one gentle next step.'
            as='h1'
          />
        </Stack>

        {!dismissed ? (
          <Surface>
            <Stack gap={3}>
              <Inline justify='space-between' align='center'>
                <strong>Privacy, plainly</strong>
                <GhostButton onClick={() => setDismissed(true)}>Dismiss</GhostButton>
              </Inline>
              <p style={{ margin: 0 }}>
                Mood check-ins, journal entries, and safety plans are stored by NOUS so you can
                revisit them later. Crisis resources are loaded from an always-accessible endpoint.
                You control what you share.
              </p>
            </Stack>
          </Surface>
        ) : null}

        <Surface>
          <Stack gap={3}>
            <Inline justify='space-between' align='center'>
              <strong>Last 7 days</strong>
              {avg != null ? <Meta>Average: {avg.toFixed(1)}/10</Meta> : null}
            </Inline>
            {loading ? <p style={{ margin: 0 }}>Loading…</p> : null}
            {!loading && last7.length === 0 ? (
              <p style={{ margin: 0 }}>
                No check-ins yet. If you’d like, start with a 30-second mood check-in—just enough to
                be seen.
              </p>
            ) : null}
            {!loading && last7.length > 0 ? (
              <MoodSparkline values={last7.map((i) => i.mood)} />
            ) : null}
          </Stack>
        </Surface>

        <Stack gap={3}>
          <CardLink to='/mood'>
            <Surface>
              <Stack gap={2}>
                <strong>Check in (~30 seconds)</strong>
                <Small>Fast mood log with optional context.</Small>
              </Stack>
            </Surface>
          </CardLink>

          <CardLink to='/journal'>
            <Surface>
              <Stack gap={2}>
                <strong>Write it out (~3 minutes)</strong>
                <Small>Free write or a guided thought record.</Small>
              </Stack>
            </Surface>
          </CardLink>

          <CardLink to='/talk'>
            <Surface>
              <Stack gap={2}>
                <strong>Talk to NOUS</strong>
                <Small>A calm conversation space.</Small>
              </Stack>
            </Surface>
          </CardLink>
        </Stack>

        {mode === 'structured' ? (
          <Surface>
            <Stack gap={2}>
              <strong>Structured view</strong>
              <Small>
                You’re in Structured mode. More insights will appear across Mood and Journal as you
                use the tools.
              </Small>
            </Stack>
          </Surface>
        ) : null}
      </Stack>
    </Page>
  );
}

function toChronological(items: MoodItem[]) {
  return [...items].reverse();
}

function MoodSparkline({ values }: { values: number[] }) {
  const w = 260;
  const h = 56;
  const pad = 6;
  const max = 10;
  const min = 1;
  const xs = values.map((_, i) => (values.length === 1 ? w / 2 : (i / (values.length - 1)) * w));
  const ys = values.map((v) => {
    const clamped = Math.max(min, Math.min(max, Number(v) || 5));
    const t = (clamped - min) / (max - min);
    return h - pad - t * (h - pad * 2);
  });
  const d = xs
    .map((x, i) => `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${ys[i].toFixed(1)}`)
    .join(' ');

  return (
    <svg
      width='100%'
      viewBox={`0 0 ${w} ${h}`}
      role='img'
      aria-label='Mood trend for the last 7 days'
    >
      <path d={d} fill='none' stroke='currentColor' strokeWidth='2' />
    </svg>
  );
}

const Meta = styled.div`
  color: ${({ theme }) => theme.colors.text.muted};
  font-size: ${({ theme }) => theme.typography.sizes.small};
`;

const Small = styled.div`
  color: ${({ theme }) => theme.colors.text.muted};
  font-size: ${({ theme }) => theme.typography.sizes.small};
`;

const CardLink = styled(Link)`
  text-decoration: none;
  color: inherit;
  display: block;
`;
