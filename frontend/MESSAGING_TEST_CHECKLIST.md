# ✅ Messaging Frontend - Testing Checklist

**Date:** August 3, 2026  
**Feature:** Real-time Messaging System

---

## 🎯 Pre-Testing Setup

- [ ] Backend server running on http://localhost:8000
- [ ] Frontend dev server running on http://localhost:3000
- [ ] At least 2 test user accounts created
- [ ] Logged in as test user #1

---

## 📋 Test Scenarios

### 1. **Initial Load**

**Conversations List:**
- [ ] Page loads without errors
- [ ] Conversations list displays
- [ ] Search bar is visible
- [ ] "New Conversation" button present
- [ ] Loading spinner shows while fetching

**Expected Result:** Empty state OR existing conversations show

---

### 2. **View Existing Conversations**

- [ ] Conversations show participant avatar (or initial)
- [ ] Last message preview displays correctly
- [ ] Unread count badge visible (if any unread)
- [ ] Timestamp shows relative time (e.g., "5 minutes ago")
- [ ] Hover effect works on conversation items

**Expected Result:** All conversation data renders properly

---

### 3. **Search Conversations**

- [ ] Type in search box
- [ ] Results appear after ~300ms delay
- [ ] Matching conversations filter correctly
- [ ] "No results" message shows if nothing matches
- [ ] Clear search returns full list

**Test Query:** Type existing participant name

**Expected Result:** Filtered list with matching conversations

---

### 4. **Select Conversation**

- [ ] Click on a conversation
- [ ] Chat window loads on right side (desktop)
- [ ] Messages history displays
- [ ] Participant header shows name and avatar
- [ ] Online indicator appears (green dot)
- [ ] Conversation highlights in list
- [ ] Auto-scrolls to bottom of messages

**Expected Result:** Full chat interface loads with message history

---

### 5. **Send Message (WebSocket)**

- [ ] Type message in input field
- [ ] Send button enables
- [ ] Press Enter OR click Send button
- [ ] Message appears instantly in chat
- [ ] Message shows on right side (own message)
- [ ] Timestamp displays
- [ ] Input field clears after sending
- [ ] WebSocket status shows "Real-time enabled"

**Test Message:** "Hello! This is a test message."

**Expected Result:** Message appears immediately, sent via WebSocket

---

### 6. **Receive Message (Real-time)**

**Setup:** Open app in TWO browser windows/tabs
- Window 1: Logged in as User A
- Window 2: Logged in as User B (same conversation)

**Steps:**
- [ ] Send message from Window 1
- [ ] Message appears in Window 2 (real-time)
- [ ] Message shows on left side (other user)
- [ ] No page refresh needed

**Expected Result:** Real-time message delivery working

---

### 7. **Typing Indicator**

**Setup:** Two windows as above

**Steps:**
- [ ] Start typing in Window 1
- [ ] "Typing..." appears in Window 2 header
- [ ] Stop typing
- [ ] "Typing..." disappears after 3 seconds

**Expected Result:** Typing indicator works in real-time

---

### 8. **Read Receipts**

- [ ] Send message from User A
- [ ] View message in User B's window
- [ ] Message status changes to "Read"
- [ ] "• Read" appears in User A's message timestamp

**Expected Result:** Read receipts update correctly

---

### 9. **Create New Conversation**

- [ ] Click "New Conversation" button (plus icon)
- [ ] Modal opens
- [ ] Search input is focused
- [ ] Type at least 2 characters
- [ ] Search results appear
- [ ] Click on a user
- [ ] User details show in selected section
- [ ] Type optional initial message
- [ ] Character counter shows (X/1000)
- [ ] Click "Start Conversation"
- [ ] Modal closes
- [ ] New conversation opens in chat window
- [ ] New conversation appears in list

**Test User:** Search for an existing user

**Expected Result:** New conversation created successfully

---

### 10. **File Attachment UI**

- [ ] Click paperclip icon in chat input
- [ ] File picker opens
- [ ] Select 1-3 files (images, PDFs, etc.)
- [ ] File preview shows with name and size
- [ ] Click X to remove a file
- [ ] File removes from preview
- [ ] Try adding 6 files
- [ ] Error toast shows "Too many files"
- [ ] Try adding file >10MB
- [ ] Error toast shows "File too large"

**Note:** Actual sending not yet integrated - just UI testing

**Expected Result:** File attachment UI works correctly

---

### 11. **Mobile Responsiveness**

**Resize browser to <768px width:**

- [ ] Only conversation list shows initially
- [ ] Chat window hidden
- [ ] Click on a conversation
- [ ] Chat window slides in/shows
- [ ] Conversation list hides
- [ ] Back button (←) appears in chat header
- [ ] Click back button
- [ ] Returns to conversation list
- [ ] Touch targets are at least 44x44px

**Expected Result:** Mobile UX works smoothly

---

### 12. **Empty States**

**No Conversations:**
- [ ] Log in with brand new user
- [ ] Empty state shows icon and message
- [ ] "Start Conversation" button displays
- [ ] Click button opens new conversation modal

**No Search Results:**
- [ ] Search for "xyzabc123nonexistent"
- [ ] Empty state shows "No conversations found"
- [ ] Helpful message displays

**No Message Selected:**
- [ ] Desktop view with no conversation selected
- [ ] Center area shows empty state
- [ ] Icon and helpful text display

**Expected Result:** All empty states render properly

---

### 13. **Loading States**

- [ ] Refresh page
- [ ] Loading spinner shows while fetching conversations
- [ ] Skeleton or spinner in chat while loading messages
- [ ] "Sending..." indicator while sending message

**Expected Result:** Loading states provide feedback

---

### 14. **Error Handling**

**Stop Backend Server:**
- [ ] Try to send message
- [ ] Error toast appears
- [ ] Message NOT added to chat
- [ ] Original text preserved in input

**Invalid Conversation:**
- [ ] Manually navigate to `/messages?conversation=invalid-id`
- [ ] Error state shows
- [ ] User-friendly error message

**Expected Result:** Errors handled gracefully

---

### 15. **WebSocket Fallback**

**Simulate WebSocket Failure:**
- [ ] Stop backend WebSocket
- [ ] Try sending message
- [ ] Falls back to HTTP POST
- [ ] Warning shows: "Real-time messaging unavailable"
- [ ] Message still sends successfully

**Expected Result:** HTTP fallback works

---

### 16. **Performance**

- [ ] Conversations list loads in <2 seconds
- [ ] Messages load in <1 second
- [ ] Search results appear within 300ms of typing
- [ ] Scrolling is smooth
- [ ] No UI freezes or stuttering
- [ ] WebSocket reconnects automatically if disconnected

**Expected Result:** App is fast and responsive

---

### 17. **Keyboard Navigation**

- [ ] Tab key navigates through focusable elements
- [ ] Enter key sends message
- [ ] Shift+Enter adds new line
- [ ] Escape closes modal
- [ ] Focus visible on all interactive elements

**Expected Result:** Keyboard navigation works

---

### 18. **Data Accuracy**

- [ ] Message timestamps are accurate
- [ ] Unread counts are correct
- [ ] Last message preview matches actual last message
- [ ] Participant info is accurate (name, avatar)
- [ ] Message order is correct (newest at bottom)

**Expected Result:** All data displays accurately

---

## 🐛 Bug Tracking

**Found Issues:**

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

## ✅ Sign-Off

**Tested By:** _________________  
**Date:** _________________  
**Overall Status:** [ ] Pass  [ ] Fail  [ ] Partial  

**Notes:**
```


```

---

## 🚀 Production Readiness

- [ ] All critical tests pass
- [ ] No major bugs found
- [ ] Performance acceptable
- [ ] Mobile experience good
- [ ] Error handling works
- [ ] WebSocket + HTTP fallback functional

**Ready for Deployment:** [ ] Yes  [ ] No  [ ] With Caveats

---

**Last Updated:** August 3, 2026
