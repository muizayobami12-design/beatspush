# BeatPush Frontend - Deployment Guide

## 🌐 Deployment Options

### Option 1: Vercel (Recommended for Next.js)

Vercel is the creators of Next.js and provides the best deployment experience.

#### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

#### Step 2: Login to Vercel

```bash
vercel login
```

#### Step 3: Deploy

```bash
# From the frontend directory
cd c:\Users\Asus\Desktop\beatspush\frontend

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

#### Step 4: Configure Environment Variables

In Vercel Dashboard:
1. Go to your project → Settings → Environment Variables
2. Add the following:

```
NEXT_PUBLIC_API_URL=https://beatspush-1.onrender.com
NEXT_PUBLIC_WS_URL=wss://beatspush-1.onrender.com
NEXT_PUBLIC_PAYSTACK_KEY=your_paystack_public_key
NEXT_PUBLIC_GA_ID=your_google_analytics_id
```

#### Step 5: Configure Domain (Optional)

1. Go to Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

**Production URL**: Your app will be available at `your-app.vercel.app`

---

### Option 2: Netlify

#### Step 1: Build Settings

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

#### Step 2: Deploy

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod
```

#### Step 3: Environment Variables

Add in Netlify Dashboard → Site Settings → Environment Variables

---

### Option 3: AWS Amplify

#### Step 1: Install Amplify CLI

```bash
npm install -g @aws-amplify/cli
amplify configure
```

#### Step 2: Initialize Amplify

```bash
amplify init
```

#### Step 3: Deploy

```bash
amplify add hosting
amplify publish
```

---

### Option 4: Docker + Any Cloud Provider

#### Dockerfile

```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

#### Build and Run

```bash
# Build Docker image
docker build -t beatpush-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://beatspush-1.onrender.com \
  -e NEXT_PUBLIC_WS_URL=wss://beatspush-1.onrender.com \
  beatpush-frontend
```

#### Deploy to Cloud

- **AWS ECS**: Push to ECR, deploy via ECS
- **Google Cloud Run**: Push to GCR, deploy via Cloud Run
- **Azure Container Instances**: Push to ACR, deploy via ACI
- **DigitalOcean App Platform**: Connect GitHub repo

---

## 🔐 Environment Variables

### Required Variables

```env
# Backend API URL
NEXT_PUBLIC_API_URL=https://beatspush-1.onrender.com

# WebSocket URL for real-time features
NEXT_PUBLIC_WS_URL=wss://beatspush-1.onrender.com
```

### Optional Variables

```env
# Payment Gateway
NEXT_PUBLIC_PAYSTACK_KEY=pk_test_xxx

# Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Feature Flags
NEXT_PUBLIC_ENABLE_PAYMENTS=true
NEXT_PUBLIC_ENABLE_MESSAGING=true
```

---

## 🚀 Pre-Deployment Checklist

### 1. Build Test

```bash
npm run build
npm start
```

Visit `http://localhost:3000` and verify:
- [ ] All pages load without errors
- [ ] Authentication works
- [ ] Theme toggle works
- [ ] Images load correctly
- [ ] API calls succeed

### 2. Environment Variables

- [ ] All `NEXT_PUBLIC_*` variables are set
- [ ] API URL points to production backend
- [ ] WebSocket URL is correct
- [ ] Paystack key is production key (if using payments)

### 3. Performance

```bash
# Check bundle size
npm run build

# Look for warnings about large bundles
```

- [ ] Bundle size is reasonable (<500KB first load)
- [ ] No unused dependencies
- [ ] Images are optimized

### 4. Security

- [ ] No sensitive keys in client code
- [ ] All API calls use HTTPS
- [ ] CORS is properly configured on backend
- [ ] CSP headers are set (if needed)

### 5. SEO

- [ ] Page titles are set
- [ ] Meta descriptions are set
- [ ] Open Graph tags are configured
- [ ] robots.txt is correct

---

## 🔧 Production Configuration

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output standalone for Docker
  output: 'standalone',
  
  // Image optimization
  images: {
    domains: [
      'beatspush-1.onrender.com',
      'res.cloudinary.com', // If using Cloudinary
      'storage.googleapis.com', // If using GCS
    ],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          }
        ]
      }
    ]
  },
  
  // Redirects
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/dashboard',
        permanent: true,
      },
    ]
  },
}

module.exports = nextConfig
```

---

## 📊 Monitoring

### Vercel Analytics

Automatically enabled on Vercel. View in dashboard.

### Google Analytics

Already configured via `NEXT_PUBLIC_GA_ID`.

### Error Tracking (Optional)

Add Sentry:

```bash
npm install @sentry/nextjs
```

```javascript
// sentry.client.config.js
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
});
```

---

## 🔄 CI/CD Setup

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
          NEXT_PUBLIC_WS_URL: ${{ secrets.WS_URL }}
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

---

## 🆘 Troubleshooting

### Build Errors

**Issue**: "Module not found"
- **Fix**: Run `npm install` again
- **Fix**: Delete `node_modules` and `.next`, reinstall

**Issue**: TypeScript errors
- **Fix**: Run `npm run type-check`
- **Fix**: Check types in `src/types/index.ts`

### Runtime Errors

**Issue**: API calls fail
- **Fix**: Check `NEXT_PUBLIC_API_URL` is set correctly
- **Fix**: Verify backend is running and accessible
- **Fix**: Check browser console for CORS errors

**Issue**: Images don't load
- **Fix**: Add image domain to `next.config.js`
- **Fix**: Check image URLs are valid

**Issue**: WebSocket connection fails
- **Fix**: Verify `NEXT_PUBLIC_WS_URL` uses `wss://` (not `ws://`)
- **Fix**: Check backend WebSocket endpoint is accessible

### Performance Issues

**Issue**: Slow page loads
- **Fix**: Check bundle size with `npm run build`
- **Fix**: Implement code splitting
- **Fix**: Optimize images

**Issue**: High memory usage
- **Fix**: Check for memory leaks in components
- **Fix**: Use React.memo for expensive components

---

## 📞 Support

For deployment issues:
1. Check this guide
2. Review build logs
3. Check deployment platform documentation:
   - [Vercel Docs](https://vercel.com/docs)
   - [Netlify Docs](https://docs.netlify.com)
   - [AWS Amplify Docs](https://docs.amplify.aws)

---

## 🎯 Post-Deployment

After successful deployment:

1. ✅ Test all major features
2. ✅ Verify API connections
3. ✅ Check analytics are tracking
4. ✅ Test on multiple devices/browsers
5. ✅ Monitor error rates
6. ✅ Set up uptime monitoring
7. ✅ Configure custom domain (if applicable)
8. ✅ Set up SSL certificate (usually automatic)

---

**Deployment Status**: Ready for Production ✅
**Last Updated**: 2026-08-02
