'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import aiAssistantService, {
  ChatMessage,
  PublishingDraft,
  AnalyzeResponse,
} from '@/services/aiAssistantService';
import { Upload, Send, Loader2, Sparkles } from 'lucide-react';

export default function AIPublishPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentDraft, setCurrentDraft] = useState<PublishingDraft | null>(null);
  const [analyzeResponse, setAnalyzeResponse] = useState<AnalyzeResponse | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load greeting on mount
  useEffect(() => {
    loadGreeting();
  }, []);

  const loadGreeting = async () => {
    try {
      const greeting = await aiAssistantService.getGreeting();
      addMessage('assistant', greeting.message);
    } catch (error) {
      console.error('Failed to load greeting:', error);
      addMessage(
        'assistant',
        "Hi! I'm your AI publishing assistant. Upload a beat and I'll help you publish it! 🎵"
      );
    }
  };

  const addMessage = (role: 'user' | 'assistant', content: string) => {
    setMessages((prev) => [
      ...prev,
      {
        role,
        content,
        timestamp: new Date(),
      },
    ]);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav)$/i)) {
      addMessage('assistant', 'Please upload an MP3 or WAV audio file.');
      return;
    }

    // Add user message
    addMessage('user', `[Uploaded: ${file.name}]`);

    // Show analyzing message
    addMessage('assistant', '🎧 Analyzing your beat...');
    setIsLoading(true);
    setUploadProgress(0);

    try {
      // Analyze audio
      const response = await aiAssistantService.analyzeAudio(
        file,
        undefined,
        (progress) => setUploadProgress(progress)
      );

      setAnalyzeResponse(response);
      setCurrentDraft(response.draft);

      // Stream AI response
      await streamAIResponse('analyze_uploaded', response);
    } catch (error: any) {
      console.error('Analysis failed:', error);
      addMessage(
        'assistant',
        `Sorry, I couldn't analyze that file. ${error.message || 'Please try again.'}`
      );
    } finally {
      setIsLoading(false);
      setUploadProgress(0);
    }
  };

  const streamAIResponse = async (intent: string, context: any) => {
    let currentMessage = '';

    try {
      const chatContext = {
        intent,
        audio_analysis: context.analysis,
        detected_genre: context.detected_genre,
        draft: context.draft,
      };

      for await (const chunk of aiAssistantService.chatStream(intent, chatContext)) {
        currentMessage += chunk;

        // Update last message or add new one
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            // Update existing message
            return [
              ...prev.slice(0, -1),
              {
                ...lastMessage,
                content: currentMessage,
              },
            ];
          } else {
            // Add new message
            return [
              ...prev,
              {
                role: 'assistant',
                content: currentMessage,
                timestamp: new Date(),
              },
            ];
          }
        });
      }
    } catch (error) {
      console.error('Stream error:', error);
      addMessage('assistant', 'Sorry, something went wrong. Please try again.');
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMsg = inputMessage.trim();
    setInputMessage('');
    addMessage('user', userMsg);

    // Parse command
    const command = aiAssistantService.parseCommand(userMsg);

    if (command?.type === 'confirm_publish' && currentDraft) {
      await handlePublish();
      return;
    }

    if (command?.type === 'change_price' && currentDraft) {
      const updatedDraft = aiAssistantService.updateDraft(currentDraft, {
        price: command.value,
      });
      setCurrentDraft(updatedDraft);
      addMessage(
        'assistant',
        `✅ Price updated to ${aiAssistantService.formatPrice(command.value)}\n\nAnything else you'd like to change?`
      );
      return;
    }

    if (command?.type === 'change_title' && currentDraft) {
      const updatedDraft = aiAssistantService.updateDraft(currentDraft, {
        title: command.value,
      });
      setCurrentDraft(updatedDraft);
      addMessage(
        'assistant',
        `✅ Title updated to "${command.value}"\n\nAnything else you'd like to change?`
      );
      return;
    }

    // Default: stream AI response
    setIsLoading(true);
    try {
      await streamAIResponse(userMsg, {
        audio_analysis: analyzeResponse?.analysis,
        detected_genre: analyzeResponse?.detected_genre,
        draft: currentDraft,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!currentDraft) {
      addMessage('assistant', 'Please upload a beat first!');
      return;
    }

    addMessage('user', 'Yes, publish it!');
    addMessage('assistant', '🚀 Publishing your beat...');
    setIsPublishing(true);

    try {
      const result = await aiAssistantService.publishDraft(currentDraft);

      addMessage(
        'assistant',
        `✅ **All done! Your beat is LIVE! 🎉**\n\nView: ${result.beat_url}\n\nYour social media posts are ready to share!`
      );

      // Reset
      setCurrentDraft(null);
      setAnalyzeResponse(null);
    } catch (error: any) {
      console.error('Publish failed:', error);
      addMessage(
        'assistant',
        `Sorry, publishing failed: ${error.message || 'Please try again.'}`
      );
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur-lg rounded-t-2xl p-6 border-b border-white/10">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">
                AI Publishing Assistant
              </h1>
              <p className="text-gray-300 text-sm">
                Upload a beat and I'll handle everything!
              </p>
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="bg-white/5 backdrop-blur-lg p-6 space-y-4 h-[600px] overflow-y-auto">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl p-4 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                    : 'bg-white/10 text-gray-100'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className="text-xs opacity-60 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white/10 rounded-2xl p-4 flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                <span className="text-gray-300">AI is thinking...</span>
              </div>
            </div>
          )}

          {uploadProgress > 0 && uploadProgress < 100 && (
            <div className="flex justify-start">
              <div className="bg-white/10 rounded-2xl p-4 w-64">
                <div className="text-gray-300 text-sm mb-2">
                  Uploading: {uploadProgress}%
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white/10 backdrop-blur-lg rounded-b-2xl p-6 border-t border-white/10">
          <div className="flex items-center space-x-3">
            {/* Upload Button */}
            <Button
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading || isPublishing}
              className="bg-white/10 hover:bg-white/20 text-white"
            >
              <Upload className="w-5 h-5" />
            </Button>

            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*,.mp3,.wav"
              onChange={handleFileSelect}
              className="hidden"
            />

            {/* Message Input */}
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type a message... (or upload a beat)"
              disabled={isLoading || isPublishing}
              className="flex-1 bg-white/5 border-white/10 text-white placeholder:text-gray-400"
            />

            {/* Send Button */}
            <Button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading || isPublishing}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:opacity-90"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>

          {/* Quick Actions */}
          {currentDraft && !isPublishing && (
            <div className="mt-4 flex space-x-2">
              <Button
                onClick={handlePublish}
                className="bg-gradient-to-r from-green-500 to-emerald-500 hover:opacity-90"
              >
                🚀 Publish Now
              </Button>
              <Button
                onClick={() => {
                  addMessage('user', 'Let me edit first');
                  addMessage(
                    'assistant',
                    'Sure! What would you like to change? (title, price, description, tags, genre)'
                  );
                }}
                variant="outline"
                className="border-white/20 text-white hover:bg-white/10"
              >
                ✏️ Edit First
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
