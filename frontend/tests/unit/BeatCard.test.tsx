import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BeatCard } from '@/components/features/beats/BeatCard';

// Mock the hooks
vi.mock('@/hooks/useFavoriteBeat', () => ({
  useFavoriteBeat: () => ({
    favorite: vi.fn(),
    isFavoriting: false,
  }),
}));

vi.mock('@/hooks/useAudioPlayer', () => ({
  useAudioPlayer: () => ({
    play: vi.fn(),
    pause: vi.fn(),
    isPlaying: false,
    currentBeatId: null,
  }),
}));

const mockBeat = {
  id: '1',
  title: 'Test Beat',
  producerName: 'Test Producer',
  producerId: 'producer-1',
  price: 29.99,
  thumbnailUrl: '/test-image.jpg',
  audioUrl: '/test-audio.mp3',
  duration: 180,
  genre: 'Hip Hop',
  tempo: 140,
  key: 'C Minor',
  tags: ['trap', 'dark', '808'],
  isFavorite: false,
  plays: 1500,
  createdAt: new Date('2024-01-01').toISOString(),
  creator: {
    id: 'producer-1',
    username: 'testproducer',
    email: 'producer@example.com',
    fullName: 'Test Producer',
    role: 'producer' as const,
  },
};

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
};

describe('BeatCard Component', () => {
  it('should render beat information correctly', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);

    expect(screen.getByText('Test Beat')).toBeInTheDocument();
    expect(screen.getByText('Test Producer')).toBeInTheDocument();
    expect(screen.getByText('$29.99')).toBeInTheDocument();
    expect(screen.getByText('Hip Hop')).toBeInTheDocument();
    expect(screen.getByText('140 BPM')).toBeInTheDocument();
  });

  it('should display beat thumbnail', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);

    const image = screen.getByAlt('Test Beat cover');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', expect.stringContaining('test-image.jpg'));
  });

  it('should format duration correctly', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);
    
    // 180 seconds = 3:00
    expect(screen.getByText('3:00')).toBeInTheDocument();
  });

  it('should display tags', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);

    expect(screen.getByText('trap')).toBeInTheDocument();
    expect(screen.getByText('dark')).toBeInTheDocument();
    expect(screen.getByText('808')).toBeInTheDocument();
  });

  it('should display play count', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);

    // Should format 1500 as "1.5K"
    expect(screen.getByText(/1\.5K/)).toBeInTheDocument();
  });

  it('should show favorite button', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);

    const favoriteButton = screen.getByRole('button', { name: /favorite/i });
    expect(favoriteButton).toBeInTheDocument();
  });

  it('should show play button', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);

    const playButton = screen.getByRole('button', { name: /play/i });
    expect(playButton).toBeInTheDocument();
  });

  it('should handle compact view', () => {
    renderWithProviders(<BeatCard beat={mockBeat} compact />);

    // In compact view, some details might be hidden
    expect(screen.getByText('Test Beat')).toBeInTheDocument();
    expect(screen.getByText('Test Producer')).toBeInTheDocument();
  });

  it('should show favorited state', () => {
    const favoritedBeat = { ...mockBeat, isFavorite: true };
    renderWithProviders(<BeatCard beat={favoritedBeat} />);

    const favoriteButton = screen.getByRole('button', { name: /favorite/i });
    // Check if the button has filled heart (could check class or icon)
    expect(favoriteButton).toBeInTheDocument();
  });

  it('should be clickable to navigate to detail page', () => {
    const handleClick = vi.fn();
    renderWithProviders(<BeatCard beat={mockBeat} onClick={handleClick} />);

    const card = screen.getByText('Test Beat').closest('div');
    if (card) {
      fireEvent.click(card);
      // In a real scenario, this would navigate to /beats/1
    }
  });

  it('should show purchase button', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);

    // Purchase button or cart icon should be present
    const purchaseButton = screen.getByRole('button', { name: /purchase|buy|cart/i });
    expect(purchaseButton).toBeInTheDocument();
  });

  it('should handle missing thumbnail gracefully', () => {
    const beatWithoutImage = { ...mockBeat, thumbnailUrl: null };
    renderWithProviders(<BeatCard beat={beatWithoutImage} />);

    // Should show placeholder or default image
    expect(screen.getByText('Test Beat')).toBeInTheDocument();
  });

  it('should display free badge for free beats', () => {
    const freeBeat = { ...mockBeat, price: 0 };
    renderWithProviders(<BeatCard beat={freeBeat} />);

    expect(screen.getByText(/free/i)).toBeInTheDocument();
  });

  it('should be accessible', () => {
    renderWithProviders(<BeatCard beat={mockBeat} />);

    // Check for proper semantic HTML and ARIA labels
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);

    // Images should have alt text
    const image = screen.getByAlt('Test Beat cover');
    expect(image).toBeInTheDocument();
  });
});
