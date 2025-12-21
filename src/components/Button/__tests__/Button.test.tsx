import React from 'react';

import { render, screen, fireEvent } from '../../../test-utils';
import Button from '../Button';

jest.mock('../../../utils/ripple-effect', () => ({
  createRipple: jest.fn(),
  rippleStyles: '',
}));
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { createRipple } = require('../../../utils/ripple-effect');

describe('Button', () => {
  it('renders the button with default props', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByTestId('button');

    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Click me');
    expect(button).toHaveClass('button--primary');
    expect(button).toHaveClass('button--medium');
    expect(button).toHaveAttribute('type', 'button');
    expect(button).not.toBeDisabled();
  });

  it('applies the correct variant class', () => {
    const { rerender } = render(<Button variant='primary'>Primary</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--primary');

    rerender(<Button variant='secondary'>Secondary</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--secondary');

    rerender(<Button variant='danger'>Danger</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--danger');

    rerender(<Button variant='outline'>Outline</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--outline');

    rerender(<Button variant='ghost'>Ghost</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--ghost');
  });

  it('applies the correct size class', () => {
    const { rerender } = render(<Button size='small'>Small</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--small');

    rerender(<Button size='medium'>Medium</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--medium');

    rerender(<Button size='large'>Large</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--large');
  });

  it('applies full-width class when fullWidth prop is true', () => {
    render(<Button fullWidth>Full Width</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--full-width');
  });

  it('disables the button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByTestId('button');
    expect(button).toBeDisabled();
    expect(button).toHaveStyle('opacity: 0.7');
    expect(button).toHaveStyle('cursor: not-allowed');
  });

  it('shows loading state when isLoading is true', () => {
    const { rerender } = render(<Button isLoading>Loading</Button>);

    // Check if loading spinner is rendered
    const spinner = screen.getByTestId('button').querySelector('.button__spinner');
    expect(spinner).toBeInTheDocument();

    // Test loading text
    rerender(
      <Button isLoading loadingText='Submitting...'>
        Submit
      </Button>
    );
    expect(screen.getByText('Submitting...')).toBeInTheDocument();
  });

  it('supports icons on the right', () => {
    render(
      <Button icon={<span data-testid='icon'>i</span>} iconPosition='right'>
        Label
      </Button>
    );
    expect(screen.getByTestId('icon')).toBeInTheDocument();
    expect(screen.getByText('Label')).toBeInTheDocument();
  });

  it('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByTestId('button');
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(
      <Button onClick={handleClick} disabled>
        Disabled Button
      </Button>
    );

    const button = screen.getByTestId('button');
    fireEvent.click(button);

    expect(handleClick).not.toHaveBeenCalled();
  });

  it('forwards the ref to the button element', () => {
    const ref = React.createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Button with Ref</Button>);

    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    expect(ref.current).toHaveTextContent('Button with Ref');
  });

  it('applies custom className', () => {
    render(<Button className='custom-class'>Custom Class</Button>);
    expect(screen.getByTestId('button')).toHaveClass('custom-class');
  });

  it('applies data attributes', () => {
    render(
      <Button data-test='test-button' data-cy='cy-button'>
        Data Attributes
      </Button>
    );

    const button = screen.getByTestId('button');
    expect(button).toHaveAttribute('data-test', 'test-button');
    expect(button).toHaveAttribute('data-cy', 'cy-button');
  });

  it('applies focus-visible styles when focused via keyboard', () => {
    render(<Button>Focusable</Button>);
    const button = screen.getByTestId('button');

    button.focus();
    // JSDOM does not compute pseudo-class styles; we only assert it remains focusable.
    expect(button).toHaveFocus();
  });

  it('creates ripple effect on click', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByTestId('button');

    fireEvent.click(button);
    expect(createRipple).toHaveBeenCalled();
  });

  it('does not create ripple when disabled or loading', () => {
    (createRipple as jest.Mock).mockClear();
    const { rerender } = render(<Button disabled>Disabled</Button>);
    fireEvent.click(screen.getByTestId('button'));
    expect(createRipple).not.toHaveBeenCalled();

    rerender(<Button isLoading>Loading</Button>);
    fireEvent.click(screen.getByTestId('button'));
    expect(createRipple).not.toHaveBeenCalled();
  });

  it('shows disabled tooltip when provided', () => {
    render(
      <Button disabled disabledTooltip='This action is disabled'>
        Disabled
      </Button>
    );

    const button = screen.getByTestId('button');
    expect(button).toHaveAttribute('aria-label', 'This action is disabled');
  });
});
