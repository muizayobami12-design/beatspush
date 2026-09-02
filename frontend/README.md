# BeatPush Frontend

AI-powered music promotion platform for African creators - Frontend Application

## 🎯 Current Status: 70% Complete

### ✅ Implemented Features

- **Authentication System**: Login, Register, Password Reset
- **Profile Management**: View/Edit profiles, Image uploads, Follow system
- **Beat Marketplace**: Browse, Search, Filter, Infinite scroll
- **Messaging Interface**: Conversations, Chat window (UI ready)
- **Analytics Dashboard**: Stats cards, Metrics display
- **Audio Player**: WaveSurfer.js integration
- **Theme System**: Dark/Light mode
- **Responsive Design**: Mobile-first approach

### 🚧 TODO (30% Remaining)

- API Integration (currently using mock data)
- WebSocket real-time messaging
- Beat upload functionality
- Payment integration (Paystack)
- Campaign builder
- Social feed
- Charts and data visualization
- Admin dashboard

## 🛠 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS, Shadcn UI
- **State Management**: Zustand, TanStack Query
- **Audio**: WaveSurfer.js
- **Forms**: React Hook Form, Zod validation
- **UI Components**: Radix UI primitives

## 📦 Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Edit .env.local with your values:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🚀 Development

```bash
# Start development server
npm run dev

# Or use the batch script (Windows)
START_DEV.bat

# Server runs on: http://localhost:3000
```

## 🏗 Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Auth pages (login, register)
│   │   ├── (dashboard)/       # Protected dashboard pages
│   │   ├── layout.tsx         # Root layout
│   │   └── providers.tsx      # Global providers
│   ├── components/
│   │   ├── features/          # Feature-specific components
│   │   │   ├── auth/          # Auth forms
│   │   │   ├── beats/         # Beat marketplace
│   │   │   ├── profile/       # Profile components
│   │   │   ├── messaging/     # Chat components
│   │   │   └── analytics/     # Analytics components
│   │   ├── layouts/           # Layout components
│   │   ├── shared/            # Shared components
│   │   └── ui/                # UI primitives (Shadcn)
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # Utilities
│   │   ├── api/               # API client
│   │   ├── audio/             # WaveSurfer config
│   │   ├── constants.ts       # App constants
│   │   └── utils.ts           # Helper functions
│   ├── services/              # API service layers
│   │   ├── authService.ts
│   │   ├── beatService.ts
│   │   └── profileService.ts
│   ├── store/                 # Zustand stores
│   │   ├── authStore.ts
│   │   ├── themeStore.ts
│   │   └── uiStore.ts
│   ├── styles/                # Global styles
│   │   └── globals.css
│   └── types/                 # TypeScript types
│       └── index.ts
├── public/                    # Static assets
├── .env.local                 # Environment variables
├── next.config.js             # Next.js configuration
├── tailwind.config.ts         # Tailwind configuration
└── tsconfig.json              # TypeScript configuration
```

## 🔗 API Integration

The frontend connects to the BeatPush backend API:

**Backend URL**: https://beatspush-1.onrender.com

### Available Endpoints

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/profiles/{username}` - Get profile
- `PUT /api/v1/profiles/me` - Update profile
- `GET /api/v1/beats` - List beats (with filters)
- `POST /api/v1/beats` - Upload beat
- `GET /api/v1/beats/{id}` - Get beat details
- `POST /api/v1/beats/{id}/favorite` - Toggle favorite
- And 20+ more endpoints...

## 🎨 Key Features

### Authentication
- Multi-step registration wizard
- Social OAuth placeholders (Google, Facebook, Apple)
- Password strength validation
- Protected routes with middleware

### Beat Marketplace
- Advanced search with debouncing (300ms)
- Multi-filter support (genre, BPM, price, key)
- Infinite scroll pagination
- Favorite system with optimistic updates
- Audio preview with WaveSurfer.js

### Profile System
- Avatar & cover photo upload (max 2MB)
- Bio with 500 character limit
- Social media links
- Follow/unfollow functionality
- Stats display (followers, beats, plays)

### Messaging
- Conversation list with unread indicators
- Real-time chat UI (WebSocket ready)
- Message timestamps with date-fns
- File attachment UI

### Analytics
- 6 key metrics cards
- Trend indicators (up/down)
- Placeholder sections for charts

## 🔧 Configuration

### Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://beatspush-1.onrender.com
NEXT_PUBLIC_WS_URL=wss://beatspush-1.onrender.com

# Payment (Optional)
NEXT_PUBLIC_PAYSTACK_KEY=your_key_here

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=your_ga_id
```

### Theme Configuration

Custom theme colors in `tailwind.config.ts`:
- Primary: Purple gradient (#667eea → #764ba2)
- Brand colors follow BeatPush design system

## 📱 Responsive Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: ≥ 1024px
- **Large**: ≥ 1280px

All components use mobile-first design approach.

## 🧪 Testing

```bash
# Run tests (when implemented)
npm test

# Run linter
npm run lint

# Type check
npm run type-check
```

## 🚢 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Environment Variables for Production

Make sure to set all `NEXT_PUBLIC_*` variables in your deployment platform.

## 🐛 Known Issues

1. **WebSocket**: Not yet connected to backend (UI ready)
2. **Charts**: Placeholder sections, need visualization library
3. **Tests**: Not yet implemented
4. **Beat Upload**: UI not created yet
5. **Payments**: Paystack integration pending

## 📝 Next Steps

### High Priority
1. ✅ Complete API integration with real backend
2. ✅ Implement WebSocket for messaging
3. ✅ Add beat upload functionality
4. ✅ Integrate Paystack payments

### Medium Priority
5. Add charts library (recharts/chart.js)
6. Create campaign builder UI
7. Implement social feed
8. Build admin dashboard

### Low Priority
9. Add unit tests
10. Add E2E tests with Playwright
11. Optimize images and lazy loading
12. Add PWA support

## 🤝 Contributing

This is part of the BeatPush platform. See main project README for contribution guidelines.

## 📄 License

Proprietary - All rights reserved

## 🔗 Links

- **Backend Repository**: ../backend
- **API Documentation**: https://beatspush-1.onrender.com/docs
- **Design System**: See `design.md` in specs folder

---

**Last Updated**: 2026-08-02
**Version**: 0.1.0 (Beta)
**Status**: Development - 70% Complete
