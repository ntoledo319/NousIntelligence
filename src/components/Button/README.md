# Button Component

A flexible, accessible button component with support for multiple variants, sizes, icons, loading states, and more.

## Usage

```jsx
import Button from './components/Button';

// Basic usage
<Button>Click Me</Button>

// With variants
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="tertiary">Tertiary</Button>
<Button variant="danger">Danger</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>

// With sizes
<Button size="small">Small</Button>
<Button size="medium">Medium</Button>
<Button size="large">Large</Button>

// With icon
<Button icon={<SomeIcon />}>With Icon</Button>
<Button icon={<SomeIcon />} iconPosition="right">Icon Right</Button>

// Loading state
<Button isLoading>Loading...</Button>
<Button isLoading loadingText="Processing...">Submit</Button>

// Full width
<Button fullWidth>Full Width Button</Button>

// Disabled with tooltip
<Button disabled disabledTooltip="You need permission to perform this action">
  Restricted Action
</Button>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'tertiary' \| 'danger' \| 'outline' \| 'ghost'` | `'primary'` | Button visual style |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | Button size |
| `fullWidth` | `boolean` | `false` | If true, button takes full width of container |
| `isLoading` | `boolean` | `false` | Shows loading spinner |
| `loadingText` | `string` | `undefined` | Text to show during loading |
| `loadingPosition` | `'left' \| 'right'` | `'left'` | Position of loading spinner |
| `icon` | `ReactNode` | `undefined` | Icon to display |
| `iconPosition` | `'left' \| 'right'` | `'left'` | Position of icon |
| `spinner` | `ReactNode` | `undefined` | Custom loading spinner |
| `disabledTooltip` | `string` | `undefined` | Tooltip shown when button is disabled |
| `children` | `ReactNode` | Required | Button content |
| `...props` | - | - | All other button HTML attributes |

## Features

- TypeScript support with comprehensive prop types
- Accessible: follows WAI-ARIA guidelines 
- Keyboard navigation with focus-visible styling
- Ripple effect on click
- Support for icons on left or right
- Custom loading states
- Tooltips for disabled buttons
- Various sizes and styles

## Development

```bash
# Run tests
npm test -- Button

# Type check
npm run type-check
```
