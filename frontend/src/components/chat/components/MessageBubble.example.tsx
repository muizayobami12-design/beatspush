/**
 * MessageBubble Example - Demonstrating Markdown Rendering
 * 
 * This example showcases all supported markdown features:
 * - Bold (**text**)
 * - Italic (*text*)
 * - Code (`code`)
 * - Bullet lists (-)
 * - Numbered lists (1.)
 * - Headings (#, ##, ###)
 * - Links ([text](url))
 */

import React from 'react';
import { MessageBubble } from './MessageBubble';
import type { Message } from '../types';

export const MessageBubbleExamples: React.FC = () => {
  const examples: Message[] = [
    {
      id: '1',
      role: 'assistant',
      content: '**Bold text** demonstrates strong emphasis in markdown.',
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
    {
      id: '2',
      role: 'assistant',
      content: '*Italic text* shows subtle emphasis in your content.',
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
    {
      id: '3',
      role: 'assistant',
      content: 'Use `inline code` for technical terms or code snippets.',
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
    {
      id: '4',
      role: 'assistant',
      content: `Here's a bullet list:
- First item
- Second item with **bold**
- Third item with *italic*`,
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
    {
      id: '5',
      role: 'assistant',
      content: `Numbered lists work too:
1. First step
2. Second step
3. Third step`,
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
    {
      id: '6',
      role: 'assistant',
      content: `# Heading 1
## Heading 2
### Heading 3

Different heading levels for structure.`,
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
    {
      id: '7',
      role: 'assistant',
      content: 'Visit [BeatPush](https://beatpush.com) to learn more about our platform.',
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
    {
      id: '8',
      role: 'assistant',
      content: `### Complete Example

Here's a **complete example** showing *multiple features* together:

- Use \`npm install\` to install packages
- Configure your [settings](https://example.com/settings)
- Run the following commands:

1. Start the server
2. Open your browser
3. Test the functionality

**Note:** Make sure to check the *documentation* for more details!`,
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
    {
      id: '9',
      role: 'user',
      content: '**This is a user message** with markdown that *should not* be rendered.',
      timestamp: new Date(),
      conversationId: 'example',
      metadata: {},
    },
  ];

  return (
    <div className="space-y-4 p-8 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">MessageBubble Markdown Examples</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          All markdown features supported in AI assistant messages
        </p>

        <div className="space-y-4">
          {examples.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ))}
        </div>

        <div className="mt-8 p-4 bg-white dark:bg-gray-800 rounded-lg border">
          <h2 className="text-lg font-semibold mb-2">Supported Markdown Features</h2>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
            <li><strong>Bold:</strong> **text** or __text__</li>
            <li><strong>Italic:</strong> *text* or _text_</li>
            <li><strong>Code:</strong> `inline code`</li>
            <li><strong>Bullet Lists:</strong> - item or * item</li>
            <li><strong>Numbered Lists:</strong> 1. item</li>
            <li><strong>Headings:</strong> # H1, ## H2, ### H3</li>
            <li><strong>Links:</strong> [text](url)</li>
          </ul>
          
          <div className="mt-4 pt-4 border-t">
            <h3 className="font-semibold text-sm mb-2">Security Features</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              All HTML is sanitized using <code>rehype-sanitize</code> to prevent XSS attacks.
              User messages display raw content without markdown processing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubbleExamples;
