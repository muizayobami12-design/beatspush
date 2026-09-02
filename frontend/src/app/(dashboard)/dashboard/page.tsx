'use client';

import { useAuthStore } from '@/store/authStore';
import { useState, useEffect } from 'react';
import { ArtistDashboard } from '@/components/dashboards/ArtistDashboard';
import { DJDashboard } from '@/components/dashboards/DJDashboard';
import { ProducerDashboard } from '@/components/dashboards/ProducerDashboard';
import { FanDashboard } from '@/components/dashboards/FanDashboard';

const ROLES = ['artist', 'dj', 'producer', 'fan', 'admin'] as const;

export default function DashboardPage() {
  let user = useAuthStore((state) => state.user);
  const [selectedRole, setSelectedRole] = useState<string>('artist');

  // Temporary: Create mock user if none exists (for testing dashboards)
  if (!user) {
    console.log('[Dashboard] No user in store, creating mock user for testing');
    user = {
      id: 'mock-user-id',
      email: 'testuser@example.com',
      role: selectedRole as any,
      tier: 'FREE',
      full_name: 'Test User',
      username: 'testuser',
      is_active: true,
      is_verified: false,
      email_verified: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_login: new Date().toISOString(),
    } as any;
  }

  // Update role in mock user
  user.role = selectedRole as any;

  console.log('[Dashboard] User role:', user?.role);

  // Route to role-specific dashboard
  let DashboardComponent;
  switch (user?.role) {
    case 'artist':
      console.log('[Dashboard] Rendering ArtistDashboard');
      DashboardComponent = ArtistDashboard;
      break;
    case 'dj':
      console.log('[Dashboard] Rendering DJDashboard');
      DashboardComponent = DJDashboard;
      break;
    case 'producer':
      console.log('[Dashboard] Rendering ProducerDashboard');
      DashboardComponent = ProducerDashboard;
      break;
    case 'fan':
      console.log('[Dashboard] Rendering FanDashboard');
      DashboardComponent = FanDashboard;
      break;
    case 'admin':
      // Admin dashboard not implemented yet, fallback to FanDashboard
      console.log('[Dashboard] Rendering FanDashboard (Admin not yet implemented)');
      DashboardComponent = FanDashboard;
      break;
    default:
      console.log('[Dashboard] Unknown role, rendering FanDashboard');
      DashboardComponent = FanDashboard;
  }

  return (
    <div>
      {/* Role Switcher */}
      <div className="fixed top-20 right-6 z-50 bg-card rounded-lg border border-border p-4 shadow-lg">
        <p className="text-xs text-muted-foreground mb-2 font-semibold">Switch Role:</p>
        <div className="flex gap-2 flex-wrap">
          {ROLES.map((role) => (
            <button
              key={role}
              onClick={() => setSelectedRole(role)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedRole === role
                  ? 'bg-gradient-to-r from-yellow-400 to-purple-600 text-black'
                  : 'bg-muted text-foreground hover:bg-muted/80'
              }`}
            >
              {role.charAt(0).toUpperCase() + role.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Dashboard Content */}
      <DashboardComponent />
    </div>
  );
}
