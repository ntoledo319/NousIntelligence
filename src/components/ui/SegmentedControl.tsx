/**
 * SegmentedControl
 *
 * A calm, low-surprise toggle between a small number of modes (2–4).
 *
 * Accessibility: uses native buttons with `aria-pressed`.
 *
 * @context_boundary UI primitives only
 * # AI-GENERATED 2025-12-21
 */
import styled from 'styled-components';

export type SegmentedOption<T extends string> = {
  value: T;
  label: string;
};

export interface SegmentedControlProps<T extends string> {
  value: T;
  onChange: (value: T) => void;
  options: Array<SegmentedOption<T>>;
  'aria-label': string;
}

export function SegmentedControl<T extends string>({
  value,
  onChange,
  options,
  'aria-label': ariaLabel,
}: SegmentedControlProps<T>) {
  return (
    <Root role='group' aria-label={ariaLabel}>
      {options.map((opt) => {
        const selected = opt.value === value;
        return (
          <SegButton
            key={opt.value}
            type='button'
            aria-pressed={selected}
            $selected={selected}
            onClick={() => onChange(opt.value)}
          >
            {opt.label}
          </SegButton>
        );
      })}
    </Root>
  );
}

const Root = styled.div`
  display: inline-flex;
  padding: 2px;
  border-radius: ${({ theme }) => theme.radii.pill};
  background: ${({ theme }) => theme.colors.bg.soft};
  border: 1px solid ${({ theme }) => theme.colors.border.subtle};
  gap: 2px;
`;

const SegButton = styled.button<{ $selected: boolean }>`
  border: 0;
  background: ${({ theme, $selected }) => ($selected ? theme.colors.bg.elevated : 'transparent')};
  color: ${({ theme }) => theme.colors.text.default};
  border-radius: ${({ theme }) => theme.radii.pill};
  padding: ${({ theme }) => theme.space[2]} ${({ theme }) => theme.space[3]};
  font: inherit;
  font-size: ${({ theme }) => theme.typography.sizes.small};
  cursor: pointer;
  box-shadow: ${({ theme, $selected }) => ($selected ? theme.shadows.sm : 'none')};
`;
