/**
 * MessageBubble Component Tests
 * Tests for markdown rendering functionality
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageBubble } from './MessageBubble';
import type { Message } from '../types';

describe('MessageBubble - Markdown Rendering', () => {
  const createMessage = (content: string, role: 'user' | 'assistant' = 'assistant'): Message => ({
    id: '1',
    role,
    content,
    timestamp: new Date(),
    conversationId: 'test-conv',
    metadata: {},
  });

  it('renders bold text correctly', () => {
    const message = createMessage('This is **bold text**');
    render(<MessageBubble message={message} />);
    
    const boldElement = screen.getByText('bold text');
    expect(boldElement.tagName).toBe('STRONG');
  });

  it('renders italic text correctly', () => {
    const message = createMessage('This is *italic text*');
    render(<MessageBubble message={message} />);
    
    const italicElement = screen.getByText('italic text');
    expect(italicElement.tagName).toBe('EM');
  });

  it('renders inline code correctly', () => {
    const message = createMessage('This is `inline code`');
    render(<MessageBubble message={message} />);
    
    const codeElement = screen.getByText('inline code');
    expect(codeElement.tagName).toBe('CODE');
  });

  it('renders bullet lists correctly', () => {
    const message = createMessage('- Item 1\n- Item 2\n- Item 3');
    render(<MessageBubble message={message} />);
    
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(3);
  });

  it('renders numbered lists correctly', () => {
    const message = createMessage('1. First\n2. Second\n3. Third');
    render(<MessageBubble message={message} />);
    
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(3);
  });

  it('renders H1 headings correctly', () => {
    const message = createMessage('# Heading 1');
    render(<MessageBubble message={message} />);
    
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toHaveTextContent('Heading 1');
  });

  it('renders H2 headings correctly', () => {
    const message = createMessage('## Heading 2');
    render(<MessageBubble message={message} />);
    
    const heading = screen.getByRole('heading', { level: 2 });
    expect(heading).toHaveTextContent('Heading 2');
  });

  it('renders H3 headings correctly', () => {
    const message = createMessage('### Heading 3');
    render(<MessageBubble message={message} />);
    
    const heading = screen.getByRole('heading', { level: 3 });
    expect(heading).toHaveTextContent('Heading 3');
  });

  it('renders links as clickable elements', () => {
    const message = createMessage('[Click here](https://example.com)');
    render(<MessageBubble message={message} />);
    
    const link = screen.getByRole('link', { name: 'Click here' });
    expect(link).toHaveAttribute('href', 'https://example.com');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('does not render markdown for user messages', () => {
    const message = createMessage('**This should not be bold**', 'user');
    render(<MessageBubble message={message} />);
    
    // User messages should display raw content without markdown processing
    expect(screen.getByText(/\*\*This should not be bold\*\*/)).toBeInTheDocument();
  });

  it('renders complex markdown with mixed formatting', () => {
    const content = `
# Title
This is **bold** and *italic* text.

- Item 1
- Item 2

Visit [our site](https://example.com) for more info.

Here is some \`inline code\`.
    `.trim();
    
    const message = createMessage(content);
    render(<MessageBubble message={message} />);
    
    // Check for various elements
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Title');
    expect(screen.getByText('bold')).toBeInTheDocument();
    expect(screen.getByText('italic')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'our site' })).toBeInTheDocument();
    expect(screen.getByText('inline code')).toBeInTheDocument();
  });

  it('sanitizes potentially harmful HTML', () => {
    const message = createMessage('<script>alert("xss")</script>Hello');
    const { container } = render(<MessageBubble message={message} />);
    
    // rehype-sanitize should strip the script tag
    expect(container.querySelector('script')).toBeNull();
  });

  it('shows timestamp for all messages', () => {
    const message = createMessage('Test message');
    const { container } = render(<MessageBubble message={message} />);
    
    // Check for timestamp element
    const timestamp = container.querySelector('.text-xs.opacity-70');
    expect(timestamp).toBeInTheDocument();
  });
});
