/**
 * MorePage
 *
 * Settings, privacy, export/delete, labs.
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
} from '../../components/ui';
import { requestJson } from '../../services/apiClient';
import { useExperienceMode } from '../../state/experienceMode';

export function MorePage() {
  const { mode, setMode } = useExperienceMode();
  const [exportText, setExportText] = React.useState<string>('');
  const [loading, setLoading] = React.useState(false);

  const loadExport = async () => {
    setLoading(true);
    try {
      const r = await requestJson<{ ok: boolean; text: string }>('/api/v2/export/text');
      setExportText(r.text || '');
    } catch {
      setExportText('Could not export right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Page narrow>
      <Stack gap={6}>
        <SectionHeader
          title='More'
          description='Privacy, settings, and gentle personalization live here.'
        />

        <Surface>
          <Stack gap={3}>
            <strong>Experience mode</strong>
            <Small>
              Gentle reduces density. Structured shows more tools and context by default.
            </Small>
            <SegmentedControl<'gentle' | 'structured'>
              aria-label='Experience mode'
              value={mode}
              onChange={setMode}
              options={[
                { value: 'gentle', label: 'Gentle' },
                { value: 'structured', label: 'Structured' },
              ]}
            />
          </Stack>
        </Surface>

        <Surface>
          <Stack gap={3}>
            <strong>Privacy summary</strong>
            <Small>
              NOUS stores the entries you save (mood logs, journal entries, thought records, and
              safety plans). Crisis resources are available without login. You can export your
              recent data any time.
            </Small>
          </Stack>
        </Surface>

        <Surface>
          <Stack gap={3}>
            <Inline justify='space-between' align='center'>
              <strong>Export</strong>
              <PrimaryButton onClick={loadExport} isLoading={loading}>
                Generate
              </PrimaryButton>
            </Inline>
            <TextArea
              value={exportText}
              onChange={(e) => setExportText(e.target.value)}
              placeholder='Export text will appear here.'
            />
            <Small>
              This is a copy/paste bundle from recent events (`GET /api/v2/export/text`).
            </Small>
          </Stack>
        </Surface>
      </Stack>
    </Page>
  );
}

const Small = styled.div`
  color: ${({ theme }) => theme.colors.text.muted};
  font-size: ${({ theme }) => theme.typography.sizes.small};
`;
