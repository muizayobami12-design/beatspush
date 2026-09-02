# Testing Authentication - Detailed Guide

## Current Status

✅ **Backend:** Running on port 8000, login API is working
✅ **Frontend:** Running on port 3001, middleware is detecting tokens in cookies
⚠️ **Issue:** Zustand store not properly hydrating from localStorage after login

## How to Test - Step by Step

### Option 1: Use Debug Page (Recommended)

1. **Go to:** http://localhost:3001/debug
2. **You'll see:**
   - Current auth store state
   - "Test Login" button
   - Logs of all operations

3. **Click "Test Login"** button
   - This will test the entire login flow
   - Watch the logs to see what happens
   - Should show token being stored

4. **After clicking "Test Login":**
   - Check if logs show "Storing in localStorage..."
   - Check if logs show "State updated..."
   - Should see token appearing in "Auth Store State"

5. **Then go to:** http://localhost:3001/dashboard
   - Should now show the dashboard content instead of "NOT AUTHENTICATED"

### Option 2: Use Quick Login Page

1. **Go to:** http://localhost:3001/quick-login
2. **Click "Quick Login"** button
3. **You'll see the process:**
   - "Logging in..." message
   - "✅ Token stored successfully! Redirecting..."
   - Should redirect to dashboard

### Option 3: Use Regular Login Form

1. **Go to:** http://localhost:3001/login
2. **Enter:**
   - Email: `testuser@example.com`
   - Password: `TestPassword123`
3. **Click "Sign In"**
4. **Open Browser DevTools (F12):**
   - Go to Console tab
   - Look for logs starting with `[LoginForm]`, `[authStore]`
   - Should show the login process

## Browser DevTools Inspection

### Check LocalStorage:
1. Press F12 to open DevTools
2. Go to "Application" tab (or "Storage" in Firefox)
3. Click "Local Storage"
4. Look for `http://localhost:3001`
5. Should see:
   - `auth_token` - Contains JWT token
   - `user` - Contains user JSON data

### Check Cookies:
1. Press F12
2. Go to "Application" tab
3. Click "Cookies"
4. Look for `http://localhost:3001`
5. Should see:
   - `auth_token` - Contains JWT token

### Check Console Logs:
1. Press F12
2. Go to "Console" tab
3. Look for logs with these prefixes:
   - `[Middleware]` - Server-side route checks
   - `[LoginForm]` - Login form actions
   - `[authStore]` - Auth store updates
   - `[DashboardLayout]` - Dashboard hydration

## Expected Behavior Flow

### Login Success Path:
```
User clicks "Sign In"
  ↓
[LoginForm] Attempting login for: testuser@example.com
  ↓
[authStore.login] Storing in localStorage...
  ↓
[authStore] Hydration complete (in next render)
  ↓
Redirect to /dashboard
  ↓
[DashboardLayout] Auth state shows isAuthenticated: true
  ↓
Dashboard content displays ✅
```

## Troubleshooting

### If Still Seeing "NOT AUTHENTICATED":

**Step 1: Check Backend**
```powershell
# Verify backend is running
netstat -ano | Select-String "8000.*LISTEN"

# Should show something like:
# TCP    127.0.0.1:8000  0.0.0.0:0  LISTENING  12345
```

**Step 2: Test Backend API Directly**
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body (@{email="testuser@example.com"; password="TestPassword123"} | ConvertTo-Json) `
  -UseBasicParsing

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

Should show:
```json
{
  "user": {
    "id": "...",
    "email": "testuser@example.com",
    ...
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Step 3: Clear Browser Cache**
```
Ctrl+Shift+Delete → Select "Cookies and other site data" → Clear data
```

**Step 4: Check Console for Errors**
- Press F12 → Console tab
- Look for red error messages
- Share any CORS or network errors

**Step 5: Check Middleware Logs**
- When you access `/dashboard`, middleware should log: `[Middleware] /dashboard - Token: ✓`
- If it says `Token: ✗`, then cookie isn't being set

## Console Log Reference

### Successful Authentication Logs:
```
[LoginForm] Attempting login for: testuser@example.com
[LoginForm] Login successful, user: testuser@example.com
[LoginForm] Token received: eyJhbGciOiJIUzI1NiI...
[authStore.login] testuser@example.com eyJhbGciOiJIUzI1NiI...
[authStore.login] Storing in localStorage...
[authStore.login] localStorage and cookie set
[authStore] Hydration complete {user: 'testuser@example.com', token: 'eyJhbGciOiJIUzI1NiI...', isAuthenticated: true}
[Middleware] /dashboard - Token: ✓
[DashboardLayout] Direct localStorage check:
  - auth_token present: true
  - user present: true
[DashboardLayout] Auth state after hydration: {isAuthenticated: true, hasToken: true, hasUser: true}
```

### Failed Authentication Logs:
```
[LoginForm] Attempting login for: testuser@example.com
Login error: Invalid credentials...
[DashboardLayout] Direct localStorage check:
  - auth_token present: false
  - user present: false
[Middleware] /dashboard - Token: ✗
```

## Quick Test Commands

### PowerShell - Test Login API:
```powershell
# Test if backend is responding
curl http://127.0.0.1:8000/api/v1/auth/login -X POST `
  -H "Content-Type: application/json" `
  -d '{"email":"testuser@example.com","password":"TestPassword123"}'
```

### Browser - Check localStorage:
```javascript
// In browser console (F12):
console.log('Auth Token:', localStorage.getItem('auth_token'));
console.log('User:', localStorage.getItem('user'));
console.log('Cookies:', document.cookie);
```

## If Everything is Failing

Please provide:
1. Screenshot of the "NOT AUTHENTICATED" page
2. Screenshot of DevTools Console tab showing errors
3. Screenshot of DevTools Application > Local Storage
4. Screenshot of DevTools Application > Cookies
5. Output of: `netstat -ano | Select-String "8000.*LISTEN"`
6. Output of the PowerShell test command above

---

**Last Updated:** 2026-09-01
**Test Pages Available:**
- Debug: http://localhost:3001/debug
- Quick Login: http://localhost:3001/quick-login
- Regular Login: http://localhost:3001/login
- Dashboard: http://localhost:3001/dashboard
