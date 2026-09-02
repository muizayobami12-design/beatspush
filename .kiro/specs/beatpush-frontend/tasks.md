# Implementation Plan: BeatPush Frontend Application

## Overview

This implementation plan breaks down the BeatPush Frontend Application into discrete coding tasks. The application is a comprehensive React-based web application built with Next.js 14, TypeScript, Tailwind CSS, and modern state management libraries. It connects to the existing BeatPush backend API (https://beatspush-1.onrender.com) to provide a complete music promotion platform for African creators.

The implementation follows a layered approach: foundation setup → core authentication → content features → real-time messaging → advanced features → optimization. Each task is designed to build incrementally on previous work, ensuring testable progress at each step.

## Tasks

### 1. Project Foundation and Configuration

- [x] 1.1 Initialize Next.js 14 project with TypeScript and configure base structure
  - Create Next.js project using `create-next-app` with TypeScript template
  - Configure `tsconfig.json` with strict mode and path aliases (@/)
  - Set up project folder structure following the design: app/, components/, lib/, hooks/, store/, services/, types/
  - Create `.env.local` template with required environment variables (API_URL, WS_URL, PAYSTACK_KEY, GA_ID)
  - Configure `next.config.js` with image domains and security headers
  - _Requirements: 44.1, 44.2, 44.6_

- [x]* 1.2 Write unit tests for project configuration utilities
  - Test environment variable validation
  - Test path alias resolution
  - _Requirements: 45.1, 45.3_

- [x] 1.3 Set up Tailwind CSS with custom theme configuration
  - Install Tailwind CSS and configure `tailwind.config.ts` with custom breakpoints
  - Create `styles/globals.css` with CSS custom properties for light and dark themes
  - Define color palette with purple gradient brand colors (#667eea to #764ba2)
  - Set up Tailwind plugins for forms and typography
  - _Requirements: 27.6, 27.5_

- [-] 1.4 Install and configure Shadcn UI component library
  - Initialize Shadcn UI with `npx shadcn-ui@latest init`
  - Install core components: Button, Input, Select, Modal, Toast, Skeleton
  - Customize component variants to match brand design
  - _Requirements: 35.1, 35.6_

- [x] 1.5 Set up ESLint, Prettier, and Husky for code quality
  - Configure ESLint with Next.js and TypeScript rules
  - Add Prettier with formatting rules
  - Install Husky and configure pre-commit hooks for linting
  - _Requirements: 44.1_

- [x] 1.6 Configure Axios API client with interceptors
  - Create `lib/api/client.ts` with Axios instance pointing to backend URL
  - Implement request interceptor to add Authorization header with JWT token
  - Implement response interceptor to handle 401 errors and redirect to login
  - Add retry logic for network errors (max 2 retries)
  - Set request timeouts: 10s for data, 60s for uploads
  - _Requirements: 38.1, 38.2, 38.3, 38.4, 38.6_

- [x]* 1.7 Write unit tests for API client interceptors
  - Test Authorization header injection
  - Test 401 response handling and redirect
  - Test retry logic for network failures
  - _Requirements: 45.3, 45.4_

### 2. State Management and Core Infrastructure

- [x] 2.1 Create Zustand stores for client state management
  - Implement `store/authStore.ts` with user, token, login, logout, register methods
  - Implement `store/themeStore.ts` with mode toggle and persistence
  - Implement `store/uiStore.ts` for sidebar and modal state
  - Configure persist middleware for auth and theme stores
  - _Requirements: 37.1, 37.4_

- [x]* 2.2 Write unit tests for Zustand stores
  - Test auth store login/logout flows
  - Test theme store toggle functionality
  - Test UI store modal open/close
  - Test persistence to localStorage
  - _Requirements: 45.3_

- [x] 2.3 Set up TanStack Query (React Query) for server state
  - Install @tanstack/react-query and @tanstack/react-query-devtools
  - Create `lib/queryClient.ts` with default options (staleTime 5min, retry 2)
  - Wrap app with QueryClientProvider in root layout
  - Add React Query DevTools for development
  - _Requirements: 37.2, 28.5_

- [-] 2.4 Implement WebSocket manager for real-time communication
  - Create `lib/websocket/manager.ts` with WebSocket connection logic
  - Implement connect(), disconnect(), send(), on(), off() methods
  - Add reconnection logic with exponential backoff (max 5 attempts)
  - Handle WebSocket events: open, message, error, close
  - _Requirements: 12.1, 12.9_

- [x]* 2.5 Write unit tests for WebSocket manager
  - Test connection establishment
  - Test message sending and receiving
  - Test reconnection logic
  - Mock WebSocket API
  - _Requirements: 45.3_

- [x] 2.6 Create TypeScript type definitions for API models
  - Define types in `types/models.ts`: User, Profile, Beat, Message, Conversation, Campaign, Post, Comment, Notification, Analytics
  - Define types in `types/api.ts`: API request/response interfaces, error types
  - Define filter and pagination types
  - _Requirements: 44.1_

- [x] 2.7 Implement error handling utilities and error types
  - Create `types/errors.ts` with APIError, ValidationError, NetworkError, AuthenticationError classes
  - Create `lib/utils/errorHandling.ts` with error mapping and user-friendly message functions
  - _Requirements: 29.1, 29.2_

### 3. Authentication System

- [x] 3.1 Create authentication service layer
  - Implement `services/authService.ts` with login, register, logout, resetPassword methods
  - Each method calls appropriate backend API endpoint using Axios client
  - Handle token storage in authStore after successful login
  - _Requirements: 1.2, 2.1, 3.1_

- [x]* 3.2 Write integration tests for authentication service
  - Test login flow with valid credentials
  - Test login flow with invalid credentials
  - Test registration flow
  - Test password reset flow
  - Mock API responses
  - _Requirements: 45.4_

- [-] 3.3 Implement registration form with multi-step wizard
  - Create `components/features/auth/RegisterForm.tsx` with step-based flow
  - Step 1: email, password, fullName inputs with Zod validation
  - Step 2: role selection (Artist, DJ, Producer, Fan, Admin)
  - Step 3: optional profile info (bio, location)
  - Use React Hook Form for form state management
  - Display field-specific validation errors inline
  - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 36.1, 36.3_

- [x]* 3.4 Write unit tests for registration form validation
  - Test email format validation
  - Test password length validation (min 8 chars)
  - Test required field validation
  - Test form submission with valid data
  - _Requirements: 45.3_

- [-] 3.5 Implement login form with OAuth options
  - Create `components/features/auth/LoginForm.tsx` with email and password inputs
  - Add "Remember me" checkbox that persists token longer
  - Add OAuth buttons for Google, Facebook, Apple (visual only, backend handles auth)
  - Display error message for invalid credentials without revealing which field was wrong
  - Link to password reset page
  - _Requirements: 2.1, 2.2, 36.2, 36.7_

- [x]* 3.6 Write unit tests for login form
  - Test form submission with valid credentials
  - Test error display for empty fields
  - Test "Remember me" functionality
  - _Requirements: 45.3_

- [-] 3.7 Implement password reset flow components
  - Create `components/features/auth/PasswordResetRequest.tsx` for email input
  - Create `components/features/auth/PasswordResetConfirm.tsx` for token + new password
  - Display success confirmation after reset request
  - Display error for invalid/expired tokens
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3.8 Create authentication middleware for route protection
  - Implement `middleware.ts` to check JWT token for protected routes
  - Redirect unauthenticated users to /login
  - Allow public access to /login, /register, /reset-password, /[username] (public profiles)
  - _Requirements: 2.4, 41.1_

- [x] 3.9 Create authentication pages using Next.js App Router
  - Create `app/(auth)/login/page.tsx` with LoginForm
  - Create `app/(auth)/register/page.tsx` with RegisterForm
  - Create `app/(auth)/reset-password/page.tsx` with PasswordResetRequest
  - Create `app/(auth)/reset-password/confirm/page.tsx` with PasswordResetConfirm
  - Apply auth layout with centered forms and branding
  - _Requirements: 1.1, 2.1, 3.1_

- [-] 3.10 Implement AuthGuard HOC for protected components
  - Create `components/shared/AuthGuard.tsx` that wraps protected routes
  - Check authentication status from authStore
  - Redirect to login if not authenticated
  - Support role-based access control for Admin routes
  - _Requirements: 2.4, 31.1_

### 4. Theme System and Core UI Components

- [x] 4.1 Implement theme provider and toggle component
  - Create `components/ThemeProvider.tsx` that applies theme class to document.documentElement
  - Create `components/shared/ThemeToggle.tsx` button that toggles between light/dark
  - Detect system theme preference on first visit using prefers-color-scheme
  - Apply theme changes within 200ms
  - _Requirements: 27.1, 27.2, 27.3, 27.4_

- [x]* 4.2 Write unit tests for theme system
  - Test theme toggle functionality
  - Test theme persistence
  - Test system theme detection
  - _Requirements: 45.3_

- [x] 4.3 Create shared UI component library
  - Implement `components/ui/Button.tsx` with variants (primary, secondary, outline, ghost, destructive) and sizes
  - Implement `components/ui/Input.tsx` with label, error state, and prefix/suffix icons
  - Implement `components/ui/Select.tsx` with search and multi-select support
  - Implement `components/ui/Modal.tsx` with backdrop, close button, and keyboard support (Esc)
  - Implement `components/ui/Toast.tsx` with auto-dismiss and types (success, error, warning, info)
  - Implement `components/ui/Skeleton.tsx` with animated shimmer effect
  - All components must have proper ARIA labels and keyboard navigation
  - _Requirements: 34.1, 34.2, 35.1, 35.6_

- [x]* 4.4 Write unit tests for shared UI components
  - Test Button variants and disabled state
  - Test Input error state and validation
  - Test Modal open/close and keyboard navigation
  - Test Toast auto-dismiss timer
  - _Requirements: 45.3_

- [x] 4.5 Implement responsive navigation layout
  - Create `components/layouts/MainNav.tsx` with links to Home, Beats, Messages, Profile, Analytics, Settings
  - Hamburger menu for mobile (<768px) with slide-out drawer
  - Full horizontal navigation for desktop (≥1024px)
  - Include ThemeToggle and user avatar dropdown
  - Add notification bell icon with unread count badge
  - Ensure minimum 44x44px touch targets for mobile
  - _Requirements: 26.2, 26.4, 25.1_

- [x] 4.6 Create error boundary component
  - Implement `components/ErrorBoundary.tsx` that catches rendering errors
  - Display fallback UI with error message and "Try Again" button
  - Log errors to console (and optionally to Sentry)
  - _Requirements: 29.4, 29.5_

- [x] 4.7 Implement root layout with providers
  - Create `app/layout.tsx` with ThemeProvider, QueryClientProvider, and ErrorBoundary
  - Include global styles and font configuration
  - Add metadata for SEO (title template, description, viewport)
  - Include skip navigation link for accessibility
  - _Requirements: 32.1, 34.6_

### 5. User Profile System

- [-] 5.1 Create profile service layer
  - Implement `services/profileService.ts` with getProfile, updateProfile, uploadAvatar, uploadCoverPhoto methods
  - Handle image uploads with multipart/form-data
  - _Requirements: 4.1, 4.3, 4.4, 4.5_

- [x] 5.2 Create custom hook for profile data fetching
  - Implement `hooks/useProfile.ts` with React Query for fetching user profile
  - Implement `hooks/useUpdateProfile.ts` mutation hook with optimistic updates
  - Implement cache invalidation after profile updates
  - _Requirements: 4.1, 37.3, 37.5_

- [x] 5.3 Implement profile header component
  - Create `components/features/profile/ProfileHeader.tsx` displaying avatar (120px), cover photo, name, role badge, location
  - Add follow button with follower/following count
  - Display social media links as icons
  - Show edit button only for own profile
  - Responsive layout: stacked on mobile, side-by-side on desktop
  - _Requirements: 10.2, 10.4, 10.5_

- [x] 5.4 Implement profile editor form
  - Create `components/features/profile/ProfileEditor.tsx` with sections for basic info, bio, social links
  - Support avatar and cover photo upload with preview and crop
  - Enforce bio character limit (max 500 chars) with counter
  - Auto-save draft to localStorage every 30 seconds
  - Compress images before upload (max 2MB)
  - _Requirements: 4.2, 4.4, 4.5, 4.6, 39.1, 39.2, 39.3_

- [x]* 5.5 Write unit tests for profile components
  - Test profile header rendering with user data
  - Test follow button click handling
  - Test profile editor form validation
  - Test image upload and preview
  - _Requirements: 45.3_

- [x] 5.6 Create public profile pages
  - Create `app/(public)/[username]/page.tsx` for public profile view
  - Fetch profile data server-side for SEO
  - Display profile header, content grid (beats/tracks), and follower lists
  - Add Open Graph and Twitter Card meta tags
  - _Requirements: 10.1, 10.2, 10.3, 32.3, 32.4_

- [x] 5.7 Create profile settings page
  - Create `app/(dashboard)/settings/page.tsx` with ProfileEditor
  - Protected route requiring authentication
  - Display success toast after profile update
  - Handle errors with user-friendly messages
  - _Requirements: 4.1, 4.3, 4.7, 29.6_

### 6. Beat Marketplace System

- [-] 6.1 Create beat service layer
  - Implement `services/beatService.ts` with getBeats, getBeatById, uploadBeat, updateBeat, deleteBeat, favoriteBeat methods
  - Support filter parameters: search, genre, tempo range, price range, key, sortBy
  - Handle pagination (page, limit)
  - _Requirements: 5.1, 5.4, 7.6_

- [x] 6.2 Create custom hooks for beat data management
  - Implement `hooks/useBeats.ts` with React Query for paginated beat fetching
  - Implement `hooks/useBeat.ts` for single beat details
  - Implement `hooks/useFavoriteBeat.ts` mutation with optimistic updates
  - Implement `hooks/useInfiniteBeats.ts` for infinite scroll
  - _Requirements: 5.4, 9.2, 28.6_

- [x]* 6.3 Write unit tests for beat hooks
  - Test useBeats with different filters
  - Test useFavoriteBeat optimistic update and rollback
  - Test useInfiniteBeats pagination
  - Mock React Query
  - _Requirements: 45.3_

- [x] 6.4 Implement BeatCard component
  - Create `components/features/beats/BeatCard.tsx` displaying thumbnail (300x300), title, creator, price, duration, genre, tempo
  - Add play button with loading state
  - Add favorite button (heart icon) with optimistic update
  - Add quick actions: add to playlist, purchase
  - Responsive card design with hover effects
  - _Requirements: 5.1, 9.2_

- [x] 6.5 Implement BeatGrid component with infinite scroll
  - Create `components/features/beats/BeatGrid.tsx` with responsive grid layout (1/2/3/4 columns)
  - Implement infinite scroll using Intersection Observer
  - Display skeleton loading states while fetching
  - Show empty state with suggestions when no beats found
  - _Requirements: 5.2, 5.5, 5.6, 35.1_

- [ ] 6.6 Implement BeatFilters component
  - Create `components/features/beats/BeatFilters.tsx` with search input, genre multi-select, tempo slider, price slider, key selector, sort dropdown
  - Debounce search input by 300ms to avoid excessive API calls
  - Update URL query parameters when filters change
  - Persist filter state in URL for sharing
  - _Requirements: 5.3, 28.5_

- [x]* 6.7 Write unit tests for beat components
  - Test BeatCard rendering and interactions
  - Test BeatFilters debouncing and URL sync
  - Test BeatGrid infinite scroll trigger
  - _Requirements: 45.3_

- [x] 6.8 Create beats browse page
  - Create `app/(dashboard)/beats/page.tsx` with BeatFilters and BeatGrid
  - Server-side data fetching for initial beats
  - Implement loading states and error handling
  - Add page title and meta description for SEO
  - _Requirements: 5.1, 5.2, 5.4, 5.5, 32.1, 32.2_

### 7. Audio Player System

- [-] 7.1 Install and configure WaveSurfer.js for audio visualization
  - Install wavesurfer.js library
  - Create `lib/audio/wavesurfer.ts` wrapper with TypeScript types
  - Configure waveform styling with brand colors
  - _Requirements: 6.2_

- [x] 7.2 Create custom audio player hook
  - Implement `hooks/useAudioPlayer.ts` managing playback state (playing, currentTime, duration, volume)
  - Handle play, pause, seek, setVolume, stop methods
  - Support audio element ref and event listeners
  - _Requirements: 6.1, 6.3, 6.4, 6.5, 6.6_
