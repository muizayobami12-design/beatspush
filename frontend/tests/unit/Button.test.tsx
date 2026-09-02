import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button Component', () => {
  it('should render with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('should call onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should not call onClick when disabled', () => {
    const handleClick = vi.fn();
    render(
      <Button onClick={handleClick} disabled>
        Click me
      </Button>
    );
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('should have disabled attribute when disabled', () => {
    render(<Button disabled>Click me</Button>);
    const button = screen.getByText('Click me');
    expect(button).toBeDisabled();
  });

  it('should render primary variant by default', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByText('Click me');
    expect(button.className).toContain('bg-primary');
  });

  it('should render secondary variant', () => {
    render(<Button variant="secondary">Click me</Button>);
    const button = screen.getByText('Click me');
    expect(button.className).toContain('bg-secondary');
  });

  it('should render outline variant', () => {
    render(<Button variant="outline">Click me</Button>);
    const button = screen.getByText('Click me');
    expect(button.className).toContain('border');
  });

  it('should render ghost variant', () => {
    render(<Button variant="ghost">Click me</Button>);
    const button = screen.getByText('Click me');
    expect(button.className).toContain('hover:bg-muted');
  });

  it('should render destructive variant', () => {
    render(<Button variant="destructive">Delete</Button>);
    const button = screen.getByText('Delete');
    expect(button.className).toContain('bg-destructive');
  });

  it('should render small size', () => {
    render(<Button size="sm">Small</Button>);
    const button = screen.getByText('Small');
    expect(button.className).toContain('h-8');
  });

  it('should render default size', () => {
    render(<Button size="default">Default</Button>);
    const button = screen.getByText('Default');
    expect(button.className).toContain('h-9');
  });

  it('should render large size', () => {
    render(<Button size="lg">Large</Button>);
    const button = screen.getByText('Large');
    expect(button.className).toContain('h-10');
  });

  it('should accept custom className', () => {
    render(<Button className="custom-class">Click me</Button>);
    const button = screen.getByText('Click me');
    expect(button.className).toContain('custom-class');
  });

  it('should render as a link when asChild is true', () => {
    render(
      <Button asChild>
        <a href="/test">Link Button</a>
      </Button>
    );
    const link = screen.getByText('Link Button');
    expect(link.tagName).toBe('A');
    expect(link).toHaveAttribute('href', '/test');
  });

  it('should support type attribute', () => {
    render(<Button type="submit">Submit</Button>);
    const button = screen.getByText('Submit');
    expect(button).toHaveAttribute('type', 'submit');
  });

  it('should be accessible with aria-label', () => {
    render(<Button aria-label="Close dialog">X</Button>);
    const button = screen.getByLabelText('Close dialog');
    expect(button).toBeInTheDocument();
  });

  it('should handle loading state', () => {
    render(
      <Button disabled>
        <span className="animate-spin">⟳</span>
        Loading...
      </Button>
    );
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeDisabled();
  });
});
