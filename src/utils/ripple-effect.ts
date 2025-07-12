import { CSSProperties } from 'react';

export const createRipple = (event: React.MouseEvent<HTMLElement>, color = 'rgba(255, 255, 255, 0.5)') => {
  const button = event.currentTarget;
  const rect = button.getBoundingClientRect();
  
  const circle = document.createElement('span');
  const diameter = Math.max(rect.width, rect.height);
  const radius = diameter / 2;

  const style: CSSProperties = {
    width: `${diameter}px`,
    height: `${diameter}px`,
    left: `${event.clientX - rect.left - radius}px`,
    top: `${event.clientY - rect.top - radius}px`,
    position: 'absolute',
    borderRadius: '50%',
    backgroundColor: color,
    transform: 'scale(0)',
    animation: 'ripple 600ms linear',
    pointerEvents: 'none',
  };

  Object.assign(circle.style, style);

  const animationEndHandler = () => {
    circle.remove();
  };

  circle.addEventListener('animationend', animationEndHandler);
  button.appendChild(circle);
};

// Global styles for ripple effect
export const rippleStyles = `
  @keyframes ripple {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }

  .ripple-container {
    position: relative;
    overflow: hidden;
    transform: translate3d(0, 0, 0);
  }
`;
