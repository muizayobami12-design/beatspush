import { Metadata } from 'next';
import { LoginForm } from '@/components/features/auth/LoginForm';

export const metadata: Metadata = {
  title: 'Sign In | BeatPush',
  description: 'Sign in to your BeatPush account to manage your music promotion',
};

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-background to-primary/5">
      <LoginForm />
    </div>
  );
}
