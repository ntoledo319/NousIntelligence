/**
 * SafetySheet (Safety & Crisis Layer)
 *
 * Opens only by explicit user intent (no surprise modals).
 * Provides:
 * - Personal grounding quick tools
 * - Crisis resources (fetched from `/resources/api/crisis`, which is explicitly unauthenticated)
 *
 * @context_boundary UI only; backend resources come from existing routes
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import { XMarkIcon } from '@heroicons/react/24/outline';
import styled from 'styled-components';

import { requestJson } from '../../services/apiClient';
import { Inline, Stack, Surface, SectionHeader, GhostButton, PrimaryButton, TextArea } from '../ui';

type CrisisResource = {
  name?: string;
  description?: string;
  phone_number?: string;
  text_number?: string;
  url?: string;
};

export interface SafetySheetProps {
  open: boolean;
  onClose: () => void;
}

export function SafetySheet({ open, onClose }: SafetySheetProps) {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [resources, setResources] = React.useState<CrisisResource[]>([]);
  const [planLoading, setPlanLoading] = React.useState(false);
  const [planSaving, setPlanSaving] = React.useState(false);
  const [planStatus, setPlanStatus] = React.useState<string | null>(null);
  const [plan, setPlan] = React.useState({
    warningSigns: '',
    copingStrategies: '',
    people: '',
    places: '',
    professionalContacts: '',
  });

  React.useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    requestJson<{ resources?: CrisisResource[] }>('/resources/api/crisis?country=US')
      .then((j) => {
        if (cancelled) return;
        const list = Array.isArray(j?.resources) ? (j.resources as CrisisResource[]) : [];
        setResources(list);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : 'Failed to load resources');
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [open]);

  React.useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setPlanLoading(true);
    setPlanStatus(null);
    requestJson<{ ok: boolean; plan: any }>('/api/v2/safety-plan')
      .then((r) => {
        if (cancelled) return;
        const p = r.plan;
        if (p && typeof p === 'object') {
          setPlan({
            warningSigns: String(p.warningSigns ?? ''),
            copingStrategies: String(p.copingStrategies ?? ''),
            people: String(p.people ?? ''),
            places: String(p.places ?? ''),
            professionalContacts: String(p.professionalContacts ?? ''),
          });
        }
      })
      .catch(() => {
        if (cancelled) return;
      })
      .finally(() => {
        if (cancelled) return;
        setPlanLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open]);

  const savePlan = async () => {
    setPlanSaving(true);
    setPlanStatus(null);
    try {
      await requestJson('/api/v2/safety-plan', {
        method: 'POST',
        body: JSON.stringify(plan),
      });
      setPlanStatus('Saved.');
    } catch {
      setPlanStatus('Could not save right now.');
    } finally {
      setPlanSaving(false);
    }
  };

  if (!open) return null;

  return (
    <Overlay role='presentation' onClick={onClose}>
      <Sheet
        role='dialog'
        aria-modal='true'
        aria-label='Safety and crisis support'
        onClick={(e) => e.stopPropagation()}
      >
        <Inline justify='space-between' align='center'>
          <div />
          <GhostButton
            onClick={onClose}
            aria-label='Close safety panel'
            icon={<XMarkIcon width={18} height={18} />}
          >
            Close
          </GhostButton>
        </Inline>

        <Stack gap={6}>
          <SectionHeader
            title='Need help now?'
            description='You deserve support. This panel is always available and easy to exit.'
            as='h2'
          />

          <Surface>
            <Stack gap={3}>
              <h3 style={{ margin: 0 }}>Quick grounding (60 seconds)</h3>
              <p style={{ margin: 0, color: 'inherit' }}>
                Try <strong>box breathing</strong>: inhale 4 · hold 4 · exhale 4 · hold 4. Repeat 3
                times.
              </p>
            </Stack>
          </Surface>

          <Surface>
            <Stack gap={3}>
              <h3 style={{ margin: 0 }}>My safety plan</h3>
              <p style={{ margin: 0, color: 'inherit' }}>
                This is yours. Keep it simple. You can edit it any time.
              </p>

              {planLoading ? <p style={{ margin: 0 }}>Loading your plan…</p> : null}

              <Stack gap={2}>
                <strong>Early warning signs</strong>
                <TextArea
                  value={plan.warningSigns}
                  onChange={(e) => setPlan((p) => ({ ...p, warningSigns: e.target.value }))}
                  placeholder='What are your early signs you’re not okay?'
                />
              </Stack>

              <Stack gap={2}>
                <strong>Coping strategies</strong>
                <TextArea
                  value={plan.copingStrategies}
                  onChange={(e) => setPlan((p) => ({ ...p, copingStrategies: e.target.value }))}
                  placeholder='What helps even a little?'
                />
              </Stack>

              <Stack gap={2}>
                <strong>People I can contact</strong>
                <TextArea
                  value={plan.people}
                  onChange={(e) => setPlan((p) => ({ ...p, people: e.target.value }))}
                  placeholder='Names + numbers (if you want).'
                />
              </Stack>

              <Stack gap={2}>
                <strong>Places I can go</strong>
                <TextArea
                  value={plan.places}
                  onChange={(e) => setPlan((p) => ({ ...p, places: e.target.value }))}
                  placeholder='A room, a walk, a friend’s place—anything that feels safer.'
                />
              </Stack>

              <Stack gap={2}>
                <strong>Professional contacts</strong>
                <TextArea
                  value={plan.professionalContacts}
                  onChange={(e) => setPlan((p) => ({ ...p, professionalContacts: e.target.value }))}
                  placeholder='Therapist, prescriber, clinic, etc.'
                />
              </Stack>

              <Inline justify='space-between' align='center'>
                <div>{planStatus ? <span>{planStatus}</span> : null}</div>
                <PrimaryButton onClick={savePlan} isLoading={planSaving}>
                  Save plan
                </PrimaryButton>
              </Inline>
            </Stack>
          </Surface>

          <Surface>
            <Stack gap={3}>
              <h3 style={{ margin: 0 }}>Crisis resources</h3>
              <p style={{ margin: 0, color: 'inherit' }}>
                If you’re in immediate danger, call your local emergency number.
              </p>

              {loading ? <p style={{ margin: 0 }}>Loading resources…</p> : null}
              {error ? <p style={{ margin: 0 }}>Couldn’t load resources: {error}</p> : null}

              {!loading && !error ? (
                <List>
                  {resources.slice(0, 6).map((r, idx) => (
                    <li key={`${r.name ?? 'resource'}-${idx}`}>
                      <strong>{r.name ?? 'Crisis support'}</strong>
                      {r.description ? <div>{r.description}</div> : null}
                      <div>
                        {r.phone_number ? <span>Call: {r.phone_number} </span> : null}
                        {r.text_number ? <span>Text: {r.text_number}</span> : null}
                        {r.url ? (
                          <span>
                            {' '}
                            <a href={r.url} target='_blank' rel='noreferrer'>
                              Website
                            </a>
                          </span>
                        ) : null}
                      </div>
                    </li>
                  ))}
                </List>
              ) : null}

              <p style={{ margin: 0 }}>
                You can also visit <a href='/resources/crisis'>/resources/crisis</a> for a full page
                view.
              </p>
            </Stack>
          </Surface>
        </Stack>
      </Sheet>
    </Overlay>
  );
}

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  display: grid;
  place-items: end center;
  padding: ${({ theme }) => theme.space[4]};
  z-index: 50;
`;

const Sheet = styled.div`
  width: min(720px, 100%);
  max-height: 85vh;
  overflow: auto;
  background: ${({ theme }) => theme.colors.bg.main};
  border: 1px solid ${({ theme }) => theme.colors.border.subtle};
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.md};
  padding: ${({ theme }) => theme.space[6]};
`;

const List = styled.ul`
  margin: 0;
  padding-left: ${({ theme }) => theme.space[6]};
  color: ${({ theme }) => theme.colors.text.default};
  display: grid;
  gap: ${({ theme }) => theme.space[3]};

  li > div {
    color: ${({ theme }) => theme.colors.text.muted};
    margin-top: ${({ theme }) => theme.space[1]};
  }
`;
