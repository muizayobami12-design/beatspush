'use client';

import { useEffect, useState } from 'react';
import { useThemeStore } from '@/store/themeStore';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme } = useThemeStore();
  const [mounted, setMounted] = useState(false);

  // Wait for hydration
  useEffect(() => {
    setMounted(true);
  }, []);

  // Apply theme after mount
  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
    document.body.classList.remove('light', 'dark');
    document.body.classList.add(theme);
    root.setAttribute('data-theme', theme);
    
    console.log('✅ Theme applied:', theme);
  }, [theme, mounted]);

  // ALWAYS render children, even while mounting
  // This prevents blank screen if store has issues
  return <>{children}</>;
}
