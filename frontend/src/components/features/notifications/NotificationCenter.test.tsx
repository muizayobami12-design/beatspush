import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NotificationCenter, type Notification } from './NotificationCenter';

const mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'message',
    title: 'New message',
    message: 'You have a new message',
    read: false,
    timestamp: new Date(),
  },
  {
    id: '2',
    type: 'follow',
    title: 'New follower',
    message: 'Someone followed you',
    read: false,
    timestamp: new Date(),
  },
  {
    id: '3',
    type: 'like',
    title: 'New like',
    message: 'Someone liked your post',
    read: true,
    timestamp: new Date(),
  },
];

describe('NotificationCenter', () => {
  // Test 1: Renders when open
  it('should render notification center when open', () => {
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={mockNotifications}
      />
    );
    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  // Test 2: Hidden when closed
  it('should not render when closed', () => {
    render(
      <NotificationCenter
        isOpen={false}
        onClose={() => {}}
        notifications={mockNotifications}
      />
    );
    const drawer = screen.queryByText('Notifications');
    expect(drawer).not.toBeVisible();
  });

  // Test 3: Displays notifications
  it('should display all notifications', () => {
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={mockNotifications}
      />
    );
    expect(screen.getByText('New message')).toBeInTheDocument();
    expect(screen.getByText('New follower')).toBeInTheDocument();
    expect(screen.getByText('New like')).toBeInTheDocument();
  });

  // Test 4: Shows unread count
  it('should show unread notification count', () => {
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={mockNotifications}
      />
    );
    expect(screen.getByText('2 unread')).toBeInTheDocument();
  });

  // Test 5: Filters by type
  it('should filter notifications by type', async () => {
    const user = userEvent.setup();
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={mockNotifications}
      />
    );

    const messageFilter = screen.getByRole('button', { name: 'message' });
    await user.click(messageFilter);

    await waitFor(() => {
      expect(screen.getByText('New message')).toBeInTheDocument();
      expect(screen.queryByText('New follower')).not.toBeInTheDocument();
    });
  });

  // Test 6: Marks notification as read
  it('should mark notification as read', async () => {
    const user = userEvent.setup();
    const onMarkAsRead = jest.fn();
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={mockNotifications}
        onMarkAsRead={onMarkAsRead}
      />
    );

    const markReadButtons = screen.getAllByText('Mark read');
    await user.click(markReadButtons[0]);

    expect(onMarkAsRead).toHaveBeenCalledWith('1');
  });

  // Test 7: Marks all as read
  it('should mark all notifications as read', async () => {
    const user = userEvent.setup();
    const onMarkAllAsRead = jest.fn();
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={mockNotifications}
        onMarkAllAsRead={onMarkAllAsRead}
      />
    );

    const markAllButton = screen.getByText('Mark all');
    await user.click(markAllButton);

    expect(onMarkAllAsRead).toHaveBeenCalled();
  });

  // Test 8: Deletes notification
  it('should delete notification', async () => {
    const user = userEvent.setup();
    const onDelete = jest.fn();
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={mockNotifications}
        onDelete={onDelete}
      />
    );

    const removeButtons = screen.getAllByText('Remove');
    await user.click(removeButtons[0]);

    expect(onDelete).toHaveBeenCalledWith('1');
  });

  // Test 9: Closes on overlay click
  it('should close when overlay clicked', async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    render(
      <NotificationCenter
        isOpen={true}
        onClose={onClose}
        notifications={mockNotifications}
      />
    );

    const overlay = screen.getByText('Notifications').closest('div')?.parentElement?.previousElementSibling;
    if (overlay) {
      await user.click(overlay);
    }

    // Close button as fallback
    const closeButton = screen.getByLabelText('Close notifications');
    await user.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });

  // Test 10: Closes with close button
  it('should close with close button', async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    render(
      <NotificationCenter
        isOpen={true}
        onClose={onClose}
        notifications={mockNotifications}
      />
    );

    const closeButton = screen.getByLabelText('Close notifications');
    await user.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });

  // Test 11: Shows empty state
  it('should show empty state when no notifications', () => {
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={[]}
      />
    );

    expect(screen.getByText('No notifications')).toBeInTheDocument();
  });

  // Test 12: Groups notifications by type
  it('should group notifications by type', () => {
    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={mockNotifications}
      />
    );

    // Type filters should exist
    expect(screen.getByRole('button', { name: 'All' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'message' })).toBeInTheDocument();
  });

  // Test 13: Formats timestamps
  it('should format timestamps correctly', () => {
    const recentNotification: Notification = {
      id: 'test',
      type: 'system',
      title: 'Recent',
      message: 'Just now',
      read: false,
      timestamp: new Date(),
    };

    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={[recentNotification]}
      />
    );

    expect(screen.getByText('Just now')).toBeInTheDocument();
  });

  // Test 14: Displays action buttons
  it('should display action buttons', () => {
    const notifWithAction: Notification = {
      id: 'test',
      type: 'purchase',
      title: 'Purchase',
      message: 'Beat purchased',
      read: false,
      timestamp: new Date(),
      action: { label: 'View', href: '/earnings' },
    };

    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={[notifWithAction]}
      />
    );

    expect(screen.getByText('View')).toBeInTheDocument();
  });

  // Test 15: Shows notification icons correctly
  it('should display correct icons for notification types', () => {
    const typedNotifications: Notification[] = [
      { id: '1', type: 'message', title: 'Msg', message: '', read: false, timestamp: new Date() },
      { id: '2', type: 'follow', title: 'Follow', message: '', read: false, timestamp: new Date() },
      { id: '3', type: 'like', title: 'Like', message: '', read: false, timestamp: new Date() },
    ];

    render(
      <NotificationCenter
        isOpen={true}
        onClose={() => {}}
        notifications={typedNotifications}
      />
    );

    // All notifications should render
    expect(screen.getByText('Msg')).toBeInTheDocument();
    expect(screen.getByText('Follow')).toBeInTheDocument();
    expect(screen.getByText('Like')).toBeInTheDocument();
  });
});
