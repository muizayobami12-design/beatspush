import { Metadata } from 'next';
import { PasswordResetRequest } from '@/components/features/auth/PasswordResetRequest';

export const metadata: Metadata = {
  title: 'Reset Password | BeatPush',
  description: 'Reset your BeatPush account password',
};

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-background to-primary/5">
      <PasswordResetRequest />
    </div>
  );
}
