'use client';

import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';
import { ProfileEditor } from '@/components/features/profile/ProfileEditor';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  User, 
  Moon, 
  Sun, 
  Bell, 
  Lock, 
  Palette,
  Globe,
  Shield,
  CreditCard,
  Music,
  Sparkles
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function SettingsPage() {
  const { user } = useAuthStore();
  const { theme, toggleTheme, setTheme } = useThemeStore();
  const [activeTab, setActiveTab] = useState('profile');

  // Convert User to Profile type
  const profile = user ? {
    ...user,
    username: user.email.split('@')[0],
    isFollowing: false,
    followersCount: 0,
    followingCount: 0,
    beatsCount: 0,
  } : null;

  return (
    <div className="w-full min-h-screen">
      <div className="container mx-auto px-4 py-6 md:py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-6 md:mb-8">
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            Settings
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage your account, appearance, and preferences
          </p>
        </div>

        {/* Settings Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6 md:space-y-8">
          <TabsList className="grid grid-cols-2 lg:grid-cols-4 gap-2 bg-card/50 p-2 rounded-xl border border-border/40 w-full">
            <TabsTrigger 
              value="profile" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary/20 data-[state=active]:to-secondary/20 data-[state=active]:text-primary"
            >
              <User className="h-4 w-4" />
              <span className="hidden sm:inline">Profile</span>
            </TabsTrigger>
            <TabsTrigger 
              value="appearance"
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary/20 data-[state=active]:to-secondary/20 data-[state=active]:text-primary"
            >
              <Palette className="h-4 w-4" />
              <span className="hidden sm:inline">Appearance</span>
            </TabsTrigger>
            <TabsTrigger 
              value="notifications"
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary/20 data-[state=active]:to-secondary/20 data-[state=active]:text-primary"
            >
              <Bell className="h-4 w-4" />
              <span className="hidden sm:inline">Notifications</span>
            </TabsTrigger>
            <TabsTrigger 
              value="security"
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary/20 data-[state=active]:to-secondary/20 data-[state=active]:text-primary"
            >
              <Lock className="h-4 w-4" />
              <span className="hidden sm:inline">Security</span>
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            <Card className="p-6 border-border/40 bg-card/50 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20">
                  <User className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Profile Information</h2>
                  <p className="text-sm text-muted-foreground">Update your profile details and public information</p>
                </div>
              </div>
              {profile && <ProfileEditor profile={profile} onSuccess={() => {}} />}
            </Card>
          </TabsContent>

          {/* Appearance Tab */}
          <TabsContent value="appearance" className="space-y-6">
            {/* Theme Selection */}
            <Card className="p-6 border-border/40 bg-card/50 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20">
                  <Palette className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Theme</h2>
                  <p className="text-sm text-muted-foreground">Choose your preferred color scheme</p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {/* Light Mode Card */}
                <button
                  onClick={() => setTheme('light')}
                  className={cn(
                    "relative rounded-xl border-2 transition-all overflow-hidden group",
                    theme === 'light' 
                      ? "border-primary shadow-lg shadow-primary/20" 
                      : "border-border/40 hover:border-primary/50"
                  )}
                >
                  <div className="aspect-video bg-gradient-to-br from-gray-50 to-gray-100 p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                      <Sun className="h-8 w-8 text-amber-500" />
                      {theme === 'light' && (
                        <div className="h-3 w-3 rounded-full bg-primary animate-pulse" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">Light Mode</h3>
                      <p className="text-sm text-gray-600">Bright and clean interface</p>
                    </div>
                  </div>
                  {/* Preview Elements */}
                  <div className="absolute inset-0 p-6 pointer-events-none">
                    <div className="absolute top-12 right-6 space-y-2">
                      <div className="h-8 w-24 bg-emerald-500/80 rounded-lg" />
                      <div className="h-8 w-32 bg-gray-200/80 rounded-lg" />
                    </div>
                  </div>
                </button>

                {/* Dark Mode Card */}
                <button
                  onClick={() => setTheme('dark')}
                  className={cn(
                    "relative rounded-xl border-2 transition-all overflow-hidden group",
                    theme === 'dark' 
                      ? "border-primary shadow-lg shadow-primary/20" 
                      : "border-border/40 hover:border-primary/50"
                  )}
                >
                  <div className="aspect-video bg-gradient-to-br from-gray-900 to-black p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                      <Moon className="h-8 w-8 text-purple-400" />
                      {theme === 'dark' && (
                        <div className="h-3 w-3 rounded-full bg-primary animate-pulse" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-1">Dark Mode</h3>
                      <p className="text-sm text-gray-400">Easy on the eyes at night</p>
                    </div>
                  </div>
                  {/* Preview Elements */}
                  <div className="absolute inset-0 p-6 pointer-events-none">
                    <div className="absolute top-12 right-6 space-y-2">
                      <div className="h-8 w-24 bg-emerald-500/80 rounded-lg" />
                      <div className="h-8 w-32 bg-gray-800/80 rounded-lg" />
                    </div>
                  </div>
                </button>
              </div>

              {/* Quick Toggle */}
              <div className="mt-6 pt-6 border-t border-border/40">
                <Button 
                  onClick={toggleTheme}
                  variant="outline"
                  className="w-full sm:w-auto"
                >
                  {theme === 'light' ? (
                    <>
                      <Moon className="h-4 w-4 mr-2" />
                      Switch to Dark Mode
                    </>
                  ) : (
                    <>
                      <Sun className="h-4 w-4 mr-2" />
                      Switch to Light Mode
                    </>
                  )}
                </Button>
              </div>
            </Card>

            {/* Color Accent (Future Feature) */}
            <Card className="p-6 border-border/40 bg-card/50 backdrop-blur-sm opacity-50">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20">
                  <Sparkles className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Accent Color</h2>
                  <p className="text-sm text-muted-foreground">Customize your brand colors (Coming Soon)</p>
                </div>
              </div>
              <div className="grid grid-cols-6 gap-3">
                {['emerald', 'purple', 'pink', 'blue', 'amber', 'rose'].map((color) => (
                  <div key={color} className="aspect-square rounded-lg bg-gray-300 dark:bg-gray-700 cursor-not-allowed" />
                ))}
              </div>
            </Card>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications" className="space-y-6">
            <Card className="p-6 border-border/40 bg-card/50 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20">
                  <Bell className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Notification Preferences</h2>
                  <p className="text-sm text-muted-foreground">Manage how you receive notifications</p>
                </div>
              </div>

              <div className="space-y-4">
                {[
                  { label: 'Email Notifications', description: 'Receive updates via email', icon: Globe },
                  { label: 'Push Notifications', description: 'Get instant updates in your browser', icon: Bell },
                  { label: 'Beat Sales', description: 'Notify me when someone purchases my beats', icon: Music },
                  { label: 'New Followers', description: 'Notify me about new followers', icon: User },
                ].map((item) => (
                  <div key={item.label} className="flex items-start justify-between p-4 rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="flex items-start gap-3">
                      <item.icon className="h-5 w-5 text-muted-foreground mt-0.5" />
                      <div>
                        <p className="font-medium">{item.label}</p>
                        <p className="text-sm text-muted-foreground">{item.description}</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" disabled>Coming Soon</Button>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <Card className="p-6 border-border/40 bg-card/50 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20">
                  <Lock className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Security & Privacy</h2>
                  <p className="text-sm text-muted-foreground">Manage your account security settings</p>
                </div>
              </div>

              <div className="space-y-4">
                {[
                  { label: 'Change Password', description: 'Update your account password', icon: Lock },
                  { label: 'Two-Factor Authentication', description: 'Add an extra layer of security', icon: Shield },
                  { label: 'Active Sessions', description: 'Manage devices signed into your account', icon: Globe },
                  { label: 'Payment Methods', description: 'Manage your saved payment methods', icon: CreditCard },
                ].map((item) => (
                  <div key={item.label} className="flex items-start justify-between p-4 rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="flex items-start gap-3">
                      <item.icon className="h-5 w-5 text-muted-foreground mt-0.5" />
                      <div>
                        <p className="font-medium">{item.label}</p>
                        <p className="text-sm text-muted-foreground">{item.description}</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" disabled>Coming Soon</Button>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
