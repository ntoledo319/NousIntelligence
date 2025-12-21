import { createRipple } from '../ripple-effect';

describe('createRipple', () => {
  it('appends a ripple element and removes it on animationend', () => {
    const button = document.createElement('button');
    // Provide a stable layout box for calculations.
    button.getBoundingClientRect = () =>
      ({
        width: 100,
        height: 40,
        left: 10,
        top: 10,
        right: 110,
        bottom: 50,
      } as DOMRect);

    document.body.appendChild(button);

    const evt = {
      currentTarget: button,
      clientX: 30,
      clientY: 30,
    } as unknown as React.MouseEvent<HTMLElement>;

    createRipple(evt, 'rgba(0, 0, 0, 0.1)');

    const ripple = button.querySelector('span');
    expect(ripple).toBeTruthy();

    ripple?.dispatchEvent(new Event('animationend'));
    expect(button.querySelector('span')).toBeFalsy();
  });
});
