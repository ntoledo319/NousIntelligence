/**
 * Button wrappers for Lumen Harbor.
 *
 * Keep call-sites semantically meaningful: Primary/Secondary/Ghost.
 * These components intentionally wrap the existing `Button` component.
 *
 * @context_boundary UI primitives only
 * # AI-GENERATED 2025-12-21
 */
import React from 'react';

import Button, { type ButtonProps } from '../Button/Button';

export const PrimaryButton: React.FC<ButtonProps> = (props) => (
  <Button variant='primary' {...props} />
);

export const SecondaryButton: React.FC<ButtonProps> = (props) => (
  <Button variant='secondary' {...props} />
);

export const GhostButton: React.FC<ButtonProps> = (props) => <Button variant='ghost' {...props} />;
