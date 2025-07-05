import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../../../components/common/Button';
import { Heart } from 'lucide-react';

describe('Button Component', () => {
  it('renders with children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies correct variant classes', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-primary');

    rerender(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-secondary');

    rerender(<Button variant="emergency">Emergency</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-emergency');

    rerender(<Button variant="ghost">Ghost</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-ghost');

    rerender(<Button variant="outline">Outline</Button>);
    expect(screen.getByRole('button')).toHaveClass('border-2', 'border-lavender-300');
  });

  it('applies correct size classes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    expect(screen.getByRole('button')).toHaveClass('text-sm-elder', 'min-h-[48px]');

    rerender(<Button size="md">Medium</Button>);
    expect(screen.getByRole('button')).toHaveClass('text-base-elder', 'min-h-[60px]');

    rerender(<Button size="lg">Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('text-lg-elder', 'min-h-[72px]');

    rerender(<Button size="xl">Extra Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('text-xl-elder', 'min-h-[84px]');
  });

  it('disables button when disabled prop is true', () => {
    const handleClick = jest.fn();
    render(<Button disabled onClick={handleClick}>Disabled</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveClass('disabled:opacity-50');
    
    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(screen.getByText('Loading')).toBeInTheDocument();
    
    // Check for loading dots
    const loadingDots = button.querySelector('.loading-dots');
    expect(loadingDots).toBeInTheDocument();
    expect(loadingDots?.children).toHaveLength(3);
  });

  it('renders icon on the left by default', () => {
    render(<Button icon={Heart}>With Icon</Button>);
    
    const button = screen.getByRole('button');
    const icon = button.querySelector('svg');
    
    expect(icon).toBeInTheDocument();
    expect(icon?.parentElement).toHaveClass('mr-2');
  });

  it('renders icon on the right when specified', () => {
    render(<Button icon={Heart} iconPosition="right">With Icon</Button>);
    
    const button = screen.getByRole('button');
    const icon = button.querySelector('svg');
    
    expect(icon).toBeInTheDocument();
    expect(icon?.parentElement).toHaveClass('ml-2');
  });

  it('applies full width when specified', () => {
    render(<Button fullWidth>Full Width</Button>);
    expect(screen.getByRole('button')).toHaveClass('w-full');
  });

  it('applies custom className', () => {
    render(<Button className="custom-class">Custom</Button>);
    expect(screen.getByRole('button')).toHaveClass('custom-class');
  });

  it('sets correct button type', () => {
    const { rerender } = render(<Button type="submit">Submit</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');

    rerender(<Button type="reset">Reset</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'reset');

    rerender(<Button>Default</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
  });

  it('sets aria-label when provided', () => {
    render(<Button ariaLabel="Custom action">Action</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Custom action');
  });

  it('hides icon when loading', () => {
    render(<Button icon={Heart} loading>Loading</Button>);
    
    const button = screen.getByRole('button');
    const icon = button.querySelector('svg');
    
    expect(icon).not.toBeInTheDocument();
    expect(button.querySelector('.loading-dots')).toBeInTheDocument();
  });

  it('prevents click when loading', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} loading>Loading</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });
});