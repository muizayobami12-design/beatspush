'use client';

'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { ProfileHeader } from '@/components/features/profile/ProfileHeader';
import { ProfileEditor } from '@/components/features/profile/ProfileEditor';
import { Modal, ModalContent, ModalHeader, ModalTitle } from '@/components/ui/Modal';
import { SkeletonCard } from '@/components/ui/skeleton';
import { ProfileIntegration } from '@/components/chat/integrations/ProfileIntegration';
import { useChatContext } from '@/components/chat/components/ChatProvider';
import { useChatStore } from '@/components/chat/store/chatStore';
import { useToast } from '@/hooks/useToast';

export default function ProfilePage() {
  const { user } = useAuthStore();
  const { openChat } = useChatContext();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const { toast } = useToast();
  const [bioValue, setBioValue] = useState(user?.bio || '');

  // Listen for AI bio generation events
  useEffect(() => {
    const handleBioEvent = (e: Event) => {
      const event = e as CustomEvent;
      const action = event.detail?.action;
      
      openChat();
      
      setTimeout(() => {
        if (action === 'write') {
          const { sendMessage } = useChatStore.getState();
          sendMessage(
            "Generate 3 different bio variations for my artist profile. " +
            "I want them in short (50 chars), medium (150 chars), and long (300 chars) formats. " +
            "Make them professional, engaging, and authentic."
          );
        } else if (action === 'improve') {
          const { sendMessage } = useChatStore.getState();
          sendMessage(
            "Suggest improvements for my artist bio. " +
            "Make it more engaging, professional, and help it stand out to potential collaborators."
          );
        }
      }, 500);
    };

    document.addEventListener('ai:generate-bio', handleBioEvent);
    return () => document.removeEventListener('ai:generate-bio', handleBioEvent);
  }, [openChat]);

  if (!user) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
      </div>
    );
  }

  // Convert User to Profile type (they should match)
  const profile = {
    ...user,
    username: user.email.split('@')[0], // Fallback username
    isFollowing: false,
    followersCount: 0,
    followingCount: 0,
    beatsCount: 0,
  } as any;

  // Handle bio update from AI chat
  const handleBioUpdate = (bio: string, variant: 'short' | 'medium' | 'long') => {
    setBioValue(bio);
    toast({
      title: 'Bio Applied',
      description: `${variant.charAt(0).toUpperCase() + variant.slice(1)} bio has been applied to your profile editor.`,
      variant: 'success',
    });
  };

  // Handle artist statement update from AI chat
  const handleArtistStatementUpdate = (statement: string) => {
    setBioValue(statement);
    toast({
      title: 'Artist Statement Applied',
      description: 'Artist statement has been applied to your profile editor.',
      variant: 'success',
    });
  };

  return (
    <ProfileIntegration
      bio={user.bio}
      fullName={user.fullName}
      location={user.location}
      genres={profile.genres}
      socialLinks={user.socialLinks}
      beatsCount={profile.beatsCount || 0}
      followersCount={profile.followersCount || 0}
      onBioUpdate={handleBioUpdate}
      onArtistStatementUpdate={handleArtistStatementUpdate}
    >
      <div className="container mx-auto px-4 py-8 space-y-6">
        <ProfileHeader
          profile={profile}
          isOwnProfile={true}
          onEditClick={() => setIsEditModalOpen(true)}
        />

        {/* Edit Modal */}
        <Modal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)}>
          <ModalContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <ModalHeader>
              <ModalTitle>Edit Profile</ModalTitle>
            </ModalHeader>
            <ProfileEditor
              profile={profile}
              onSuccess={() => setIsEditModalOpen(false)}
              bioValue={bioValue}
              onBioChange={setBioValue}
            />
          </ModalContent>
        </Modal>

        {/* Content Tabs - to be implemented */}
        <div className="rounded-lg border border-dashed border-muted-foreground/25 p-12 text-center">
          <p className="text-lg font-medium text-muted-foreground">
            Your beats and content will appear here
          </p>
        </div>
      </div>
    </ProfileIntegration>
  );
}
