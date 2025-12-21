import { render, screen } from '../../../test-utils';
import Button from '../../Button/Button';
import ButtonGroup from '../ButtonGroup';

describe('ButtonGroup', () => {
  it('renders children correctly', () => {
    render(
      <ButtonGroup>
        <Button>Button 1</Button>
        <Button>Button 2</Button>
      </ButtonGroup>
    );

    expect(screen.getByTestId('button-group')).toBeInTheDocument();
    expect(screen.getByText('Button 1')).toBeInTheDocument();
    expect(screen.getByText('Button 2')).toBeInTheDocument();
  });

  it('applies correct direction and spacing', () => {
    const { rerender } = render(
      <ButtonGroup direction='column' spacing='large'>
        <Button>Button 1</Button>
        <Button>Button 2</Button>
      </ButtonGroup>
    );

    const group = screen.getByTestId('button-group');
    expect(group).toHaveStyle('flex-direction: column');

    rerender(
      <ButtonGroup direction='row' spacing='small' equalWidth>
        <Button>Button 1</Button>
        <Button>Button 2</Button>
      </ButtonGroup>
    );

    expect(group).toHaveStyle('flex-direction: row');
  });
});
