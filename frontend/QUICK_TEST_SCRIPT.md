# 🚀 Quick Test Script - 5 Minutes

**Goal:** Verify core functionality is working before deeper testing

---

## ⚡ Pre-Flight Check

```bash
# Terminal 1 - Backend (should already be running)
cd backend
# Check: http://localhost:8000/api/v1/docs

# Terminal 2 - Frontend
cd frontend
npm run dev
# Opens: http://localhost:3000
```

---

## ✅ 5-Minute Test Checklist

### 1. Login (30 seconds)
- [ ] Navigate to http://localhost:3000
- [ ] Login with test account
- [ ] Dashboard loads successfully

### 2. Feed - Create Post (1 minute)
- [ ] Click "Feed" in navigation
- [ ] Type: "Testing BeatPush! 🎵"
- [ ] Click "Post"
- [ ] Post appears at top instantly
- [ ] ✅ **PASS** if post shows with your name/avatar

### 3. Feed - Like Post (30 seconds)
- [ ] Click heart icon on your post
- [ ] Heart fills red
- [ ] Count changes to "1"
- [ ] Click again to unlike
- [ ] ✅ **PASS** if like toggles smoothly

### 4. Feed - Comment (1 minute)
- [ ] Click "Comment" on your post
- [ ] Modal opens
- [ ] Type: "First comment!"
- [ ] Press Enter or click Send
- [ ] Comment appears
- [ ] Close modal
- [ ] ✅ **PASS** if comment saved

### 5. Messages - Access (30 seconds)
- [ ] Click "Messages" in navigation
- [ ] Page loads (may be empty)
- [ ] Search bar visible
- [ ] "New Conversation" button visible
- [ ] ✅ **PASS** if page renders

### 6. Navigation Test (30 seconds)
- [ ] Click each nav item: Home, Feed, Beats, Messages, Analytics, Profile
- [ ] Each page loads
- [ ] No errors in console
- [ ] ✅ **PASS** if all pages accessible

### 7. Mobile View (1 minute)
- [ ] Press F12 (DevTools)
- [ ] Toggle device toolbar (Ctrl+Shift+M)
- [ ] Select iPhone or Android
- [ ] Navigation menu visible
- [ ] Feed readable and scrollable
- [ ] ✅ **PASS** if mobile looks good

---

## 🎯 Expected Results

**ALL PASS:** ✅ Ready for full testing  
**1-2 FAIL:** Minor issues, continue with caution  
**3+ FAIL:** Stop and debug issues first  

---

## 🐛 Common Issues & Fixes

### Issue: Feed page blank
**Fix:** Check backend is running on :8000

### Issue: "Failed to create post"
**Fix:** 
1. Check browser console for errors
2. Verify API_URL in .env.local
3. Check backend logs

### Issue: Modal doesn't open
**Fix:** Hard refresh (Ctrl+Shift+R)

### Issue: Navigation not working
**Fix:** 
1. Check for TypeScript errors
2. Run `npm run build` to verify

### Issue: Login fails
**Fix:**
1. Check database connection
2. Verify backend .env file
3. Create new test user

---

## 📊 Quick Test Results

```
Date: _______________
Time: _______________

✅ PASSED TESTS: ___/7

❌ FAILED TESTS:
- 
- 

NOTES:


READY FOR FULL TESTING: YES / NO
```

---

## 🚀 Next Steps

**If All Pass:**
→ Proceed to full testing guide  
→ Continue with Audio Player implementation  
→ Prepare for production deployment  

**If Issues Found:**
→ Document issues  
→ Fix critical bugs  
→ Re-run quick test  

---

**Time to Complete:** 5 minutes  
**Last Updated:** August 3, 2026
