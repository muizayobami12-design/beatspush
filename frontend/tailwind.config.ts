import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Stitch Design System - "Modern Heritage"
        // All colors from Stitch reference files
        'background': '#141313',
        'surface': '#141313',
        'surface-dim': '#141313',
        'surface-bright': '#3a3939',
        'surface-container-lowest': '#0e0e0e',
        'surface-container-low': '#1c1b1b',
        'surface-container': '#201f1f',
        'surface-container-high': '#2b2a2a',
        'surface-container-highest': '#353434',
        'surface-variant': '#353434',
        'surface-tint': '#c9c6c5',
        
        'primary': '#c9c6c5',
        'primary-fixed': '#e5e2e1',
        'primary-fixed-dim': '#c9c6c5',
        'primary-container': '#0d0d0d',
        'on-primary': '#313030',
        'on-primary-fixed': '#1c1b1b',
        'on-primary-fixed-variant': '#474646',
        'on-primary-container': '#7c7a7a',
        
        'secondary': '#e9c349',
        'secondary-fixed': '#ffe088',
        'secondary-fixed-dim': '#e9c349',
        'secondary-container': '#af8d11',
        'on-secondary': '#3c2f00',
        'on-secondary-fixed': '#241a00',
        'on-secondary-fixed-variant': '#574500',
        'on-secondary-container': '#342800',
        
        'tertiary': '#f4bb92',
        'tertiary-fixed': '#ffdcc5',
        'tertiary-fixed-dim': '#f4bb92',
        'tertiary-container': '#1a0800',
        'on-tertiary': '#4a280a',
        'on-tertiary-fixed': '#301400',
        'on-tertiary-fixed-variant': '#653d1e',
        'on-tertiary-container': '#a0704d',
        
        'error': '#ffb4ab',
        'error-container': '#93000a',
        'on-error': '#690005',
        'on-error-container': '#ffdad6',
        
        'on-background': '#e5e2e1',
        'on-surface': '#e5e2e1',
        'on-surface-variant': '#c4c7c7',
        
        'outline': '#8e9192',
        'outline-variant': '#444748',
        
        'inverse-surface': '#e5e2e1',
        'inverse-primary': '#5f5e5e',
        'inverse-on-surface': '#313030',
        
        // Safari Clay (custom accent for borders)
        'safari-clay': '#8B5E3C',
        
        /* Keep existing CSS Variables support for compatibility */
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        foreground: 'hsl(var(--foreground))',
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      fontFamily: {
        'display-lg': ['Playfair Display', 'serif'],
        'headline-lg': ['Playfair Display', 'serif'],
        'headline-md': ['Playfair Display', 'serif'],
        'headline-lg-mobile': ['Playfair Display', 'serif'],
        'body-lg': ['Inter', 'sans-serif'],
        'body-md': ['Inter', 'sans-serif'],
        'label-sm': ['Inter', 'sans-serif'],
      },
      fontSize: {
        'display-lg': ['64px', { lineHeight: '72px', fontWeight: '700', letterSpacing: '-0.02em' }],
        'headline-lg': ['40px', { lineHeight: '48px', fontWeight: '600' }],
        'headline-md': ['28px', { lineHeight: '36px', fontWeight: '500' }],
        'headline-lg-mobile': ['32px', { lineHeight: '40px', fontWeight: '600' }],
        'body-lg': ['18px', { lineHeight: '28px', fontWeight: '400' }],
        'body-md': ['16px', { lineHeight: '24px', fontWeight: '400' }],
        'label-sm': ['12px', { lineHeight: '16px', fontWeight: '600', letterSpacing: '0.05em' }],
      },
      spacing: {
        'unit': '8px',
        'margin-mobile': '20px',
        'gutter': '24px',
        'stack-lg': '48px',
        'stack-sm': '12px',
        'container-max': '1280px',
        'margin-desktop': '64px',
        'stack-md': '24px',
        'sidebar-width': '280px',
      },
      borderRadius: {
        'DEFAULT': '0.125rem',
        'lg': '0.25rem',
        'xl': '0.5rem',
        'full': '0.75rem',
      },
      backgroundImage: {
        'gradient-overlay': 'linear-gradient(to bottom, rgba(20, 19, 19, 0.6), rgba(20, 19, 19, 1))',
        'gradient-overlay-right': 'linear-gradient(to right, rgba(20, 19, 19, 0.9) 0%, rgba(20, 19, 19, 0.4) 100%)',
      },
      backdropFilter: {
        'glass': 'blur(12px)',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.3)',
      },
    },
  },
  plugins: [],
};

export default config;
