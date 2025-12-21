/**
 * JournalPage (Thought Workbench)
 *
 * Free Write + Guided Tools (Thought Record).
 *
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import styled from 'styled-components';

import {
  Inline,
  Page,
  PrimaryButton,
  SectionHeader,
  SegmentedControl,
  Stack,
  Surface,
  TextArea,
  TextField,
} from '../../components/ui';
import { useLocalStorageState } from '../../hooks/useLocalStorageState';
import { requestJson } from '../../services/apiClient';

type Tab = 'free' | 'guided';

type ThoughtRecordDraft = {
  situation: string;
  thoughts: string;
  emotions: string;
  intensity: number;
  evidence_for: string;
  evidence_against: string;
  alternative_thought: string;
};

export function JournalPage() {
  const [tab, setTab] = React.useState<Tab>('free');
  const [draft, setDraft] = useLocalStorageState<string>('lumen.journalDraft', '');
  const [status, setStatus] = React.useState<string>('Draft');
  const [saving, setSaving] = React.useState(false);

  const saveFreeWrite = async () => {
    if (!draft.trim()) return;
    setSaving(true);
    setStatus('Saving…');
    try {
      await requestJson('/api/v2/journal/append', {
        method: 'POST',
        body: JSON.stringify({ text: draft, tags: [] }),
      });
      setStatus('Saved just now');
      setDraft('');
    } catch {
      setStatus('Could not save right now');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Page narrow>
      <Stack gap={6}>
        <SectionHeader
          title='Journal'
          description='A private space to write it out, or use a gentle tool.'
        />
        <SegmentedControl<Tab>
          aria-label='Journal mode'
          value={tab}
          onChange={setTab}
          options={[
            { value: 'free', label: 'Free write' },
            { value: 'guided', label: 'Guided tools' },
          ]}
        />

        {tab === 'free' ? (
          <Stack gap={3}>
            <PromptSurface>
              <strong>What’s on your mind?</strong>
              <Small>Write a little or a lot. You can stop anytime.</Small>
            </PromptSurface>

            <Surface>
              <Stack gap={3}>
                <TextArea
                  placeholder='Start with one sentence. That’s enough.'
                  value={draft}
                  onChange={(e) => {
                    setDraft(e.target.value);
                    setStatus('Draft');
                  }}
                />

                <Inline justify='space-between' align='center'>
                  <Small role='status'>{status}</Small>
                  <PrimaryButton
                    onClick={saveFreeWrite}
                    isLoading={saving}
                    disabled={!draft.trim()}
                  >
                    Save
                  </PrimaryButton>
                </Inline>
              </Stack>
            </Surface>
          </Stack>
        ) : (
          <ThoughtRecordWizard />
        )}
      </Stack>
    </Page>
  );
}

function ThoughtRecordWizard() {
  const [step, setStep] = React.useState(0);
  const [form, setForm] = React.useState<ThoughtRecordDraft>({
    situation: '',
    thoughts: '',
    emotions: '',
    intensity: 6,
    evidence_for: '',
    evidence_against: '',
    alternative_thought: '',
  });
  const [saving, setSaving] = React.useState(false);
  const [status, setStatus] = React.useState<string | null>(null);

  const steps = [
    {
      title: 'Situation',
      body: (
        <TextArea
          placeholder='What happened? Just the facts.'
          value={form.situation}
          onChange={(e) => setForm((p) => ({ ...p, situation: e.target.value }))}
        />
      ),
    },
    {
      title: 'Thought',
      body: (
        <TextArea
          placeholder='What did your mind say in that moment?'
          value={form.thoughts}
          onChange={(e) => setForm((p) => ({ ...p, thoughts: e.target.value }))}
        />
      ),
    },
    {
      title: 'Emotion & intensity',
      body: (
        <Stack gap={3}>
          <TextField
            placeholder='Emotion(s), e.g., anxious, sad, angry'
            value={form.emotions}
            onChange={(e) => setForm((p) => ({ ...p, emotions: e.target.value }))}
            aria-label='Emotions'
          />
          <Inline justify='space-between' align='center'>
            <Small>Intensity (1–10)</Small>
            <Small>{form.intensity}/10</Small>
          </Inline>
          <input
            type='range'
            min={1}
            max={10}
            step={1}
            value={form.intensity}
            onChange={(e) => setForm((p) => ({ ...p, intensity: Number(e.target.value) }))}
            aria-label='Emotion intensity'
          />
        </Stack>
      ),
    },
    {
      title: 'Evidence',
      body: (
        <Stack gap={3}>
          <TextArea
            placeholder='Evidence for the thought'
            value={form.evidence_for}
            onChange={(e) => setForm((p) => ({ ...p, evidence_for: e.target.value }))}
          />
          <TextArea
            placeholder='Evidence against the thought'
            value={form.evidence_against}
            onChange={(e) => setForm((p) => ({ ...p, evidence_against: e.target.value }))}
          />
        </Stack>
      ),
    },
    {
      title: 'Alternative thought',
      body: (
        <TextArea
          placeholder='A kinder, more balanced thought (even if you only partly believe it).'
          value={form.alternative_thought}
          onChange={(e) => setForm((p) => ({ ...p, alternative_thought: e.target.value }))}
        />
      ),
    },
  ];

  const canNext =
    (step === 0 && form.situation.trim()) ||
    (step === 1 && form.thoughts.trim()) ||
    (step === 2 && form.emotions.trim()) ||
    step > 2;

  const save = async () => {
    setSaving(true);
    setStatus(null);
    try {
      await requestJson('/api/v2/thought-record/create', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          emotions: form.emotions
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean),
        }),
      });
      setStatus('Saved. You can come back to this later.');
      setStep(0);
      setForm({
        situation: '',
        thoughts: '',
        emotions: '',
        intensity: 6,
        evidence_for: '',
        evidence_against: '',
        alternative_thought: '',
      });
    } catch {
      setStatus('Could not save right now.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Surface>
      <Stack gap={4}>
        <Inline justify='space-between' align='center'>
          <strong>
            Thought record · Step {step + 1}/{steps.length}: {steps[step].title}
          </strong>
        </Inline>

        {steps[step].body}

        <Inline justify='space-between' align='center'>
          <PrimaryButton onClick={() => setStep((s) => Math.max(0, s - 1))} disabled={step === 0}>
            Back
          </PrimaryButton>

          {step < steps.length - 1 ? (
            <PrimaryButton onClick={() => setStep((s) => s + 1)} disabled={!canNext}>
              Next
            </PrimaryButton>
          ) : (
            <PrimaryButton onClick={save} isLoading={saving}>
              Save thought record
            </PrimaryButton>
          )}
        </Inline>

        {status ? <Small role='status'>{status}</Small> : null}
      </Stack>
    </Surface>
  );
}

const PromptSurface = styled(Surface)`
  background: ${({ theme }) => theme.colors.bg.soft};
`;

const Small = styled.div`
  color: ${({ theme }) => theme.colors.text.muted};
  font-size: ${({ theme }) => theme.typography.sizes.small};
`;
