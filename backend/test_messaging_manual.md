# Manual Testing Guide for BeatPush Messaging System

Since automated tests are experiencing connection issues, here's a manual testing guide using tools like Postman, Insomnia, or curl.

## Base URL
```
http://localhost:8000/api/v1
```

## Test Users
- **User 1:** `artist@test.com` / `testpass123`
- **User 2:** `dj@test.com` / `testpass123`

---

## Step 1: Login Both Users

### Login User 1
```bash
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "artist@test.com",
  "password": "testpass123"
}
```

**Save the `access_token` from response:**
```json
{
  "tokens": {
    "access_token": "eyJhbGc..."
  }
}
```

### Login User 2
```bash
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "dj@test.com",
  "password": "testpass123"
}
```

---

## Step 2: Get User IDs

### Get User 1 Info
```bash
GET http://localhost:8000/api/v1/users/me
Authorization: Bearer <USER_1_TOKEN>
```

Save the `id` field.

### Get User 2 Info
```bash
GET http://localhost:8000/api/v1/users/me
Authorization: Bearer <USER_2_TOKEN>
```

Save the `id` field.

---

## Step 3: Create Conversation

```bash
POST http://localhost:8000/api/v1/messaging/conversations
Authorization: Bearer <USER_1_TOKEN>
Content-Type: application/json

{
  "recipient_id": "<USER_2_ID>"
}
```

**Expected Response:**
```json
{
  "id": "conversation_id_here",
  "participants": [...],
  "last_message": null,
  "unread_count": 0,
  "is_message_request": false
}
```

Save the `conversation_id`.

---

## Step 4: Send Message

```bash
POST http://localhost:8000/api/v1/messaging/messages
Authorization: Bearer <USER_1_TOKEN>
Content-Type: application/json

{
  "conversation_id": "<CONVERSATION_ID>",
  "content": "Hello! This is a test message."
}
```

**Expected Response:**
```json
{
  "id": "message_id_here",
  "conversation_id": "...",
  "sender_id": "...",
  "content": "Hello! This is a test message.",
  "created_at": "...",
  "is_edited": false
}
```

---

## Step 5: Get Messages

```bash
GET http://localhost:8000/api/v1/messaging/conversations/<CONVERSATION_ID>/messages
Authorization: Bearer <USER_2_TOKEN>
```

**Expected Response:**
```json
{
  "messages": [
    {
      "id": "...",
      "content": "Hello! This is a test message.",
      "sender": {...}
    }
  ],
  "has_more": false
}
```

---

## Step 6: Mark Message as Read

```bash
POST http://localhost:8000/api/v1/messaging/messages/<MESSAGE_ID>/read
Authorization: Bearer <USER_2_TOKEN>
```

**Expected Response:**
```json
{
  "message": "Message marked as read"
}
```

---

## Step 7: Edit Message

```bash
PUT http://localhost:8000/api/v1/messaging/messages/<MESSAGE_ID>
Authorization: Bearer <USER_1_TOKEN>
Content-Type: application/json

{
  "content": "Edited: This message has been updated!"
}
```

**Expected Response:**
```json
{
  "id": "...",
  "content": "Edited: This message has been updated!",
  "is_edited": true
}
```

---

## Step 8: Test Privacy Settings

### Get Settings
```bash
GET http://localhost:8000/api/v1/messaging/settings
Authorization: Bearer <USER_1_TOKEN>
```

### Update Settings
```bash
PUT http://localhost:8000/api/v1/messaging/settings
Authorization: Bearer <USER_1_TOKEN>
Content-Type: application/json

{
  "message_filter": "everyone",
  "read_receipts_enabled": true,
  "typing_indicators_enabled": true
}
```

---

## Step 9: Test Blocking

### Block User
```bash
POST http://localhost:8000/api/v1/messaging/block
Authorization: Bearer <USER_1_TOKEN>
Content-Type: application/json

{
  "user_id": "<USER_2_ID>",
  "reason": "Testing block functionality"
}
```

### Get Blocked Users
```bash
GET http://localhost:8000/api/v1/messaging/blocked-users
Authorization: Bearer <USER_1_TOKEN>
```

### Unblock User
```bash
DELETE http://localhost:8000/api/v1/messaging/block/<USER_2_ID>
Authorization: Bearer <USER_1_TOKEN>
```

---

## Step 10: Test WebSocket Stats

```bash
GET http://localhost:8000/api/v1/ws/stats
```

**Expected Response:**
```json
{
  "status": "operational",
  "stats": {
    "total_users_online": 0,
    "total_connections": 0,
    "active_conversations": 0,
    "active_typing_indicators": 0
  }
}
```

---

## Step 11: Test List Conversations

```bash
GET http://localhost:8000/api/v1/messaging/conversations?page=1&page_size=20
Authorization: Bearer <USER_1_TOKEN>
```

---

## Step 12: Test Unread Count

```bash
GET http://localhost:8000/api/v1/messaging/unread-count
Authorization: Bearer <USER_2_TOKEN>
```

---

## Success Criteria

✅ **All endpoints should return 2xx status codes**
✅ **Message created and retrieved successfully**
✅ **Read receipts work**
✅ **Edit functionality works**
✅ **Privacy settings CRUD operations work**
✅ **Blocking/unblocking works**
✅ **WebSocket stats endpoint accessible**

---

## Postman Collection

You can import this into Postman:

1. Create a new collection called "BeatPush Messaging"
2. Create an environment with variables:
   - `base_url`: `http://localhost:8000/api/v1`
   - `user1_token`: (set after login)
   - `user2_token`: (set after login)
   - `user1_id`: (set after getting user info)
   - `user2_id`: (set after getting user info)
   - `conversation_id`: (set after creating conversation)
   - `message_id`: (set after sending message)

3. Add all the requests above using the variables

---

## WebSocket Testing

To test WebSocket connections, use a WebSocket client tool:

### Connection URL
```
ws://localhost:8000/api/v1/ws/conversations?token=<ACCESS_TOKEN>
```

### Client → Server Events

**Start Typing:**
```json
{
  "type": "typing_start",
  "conversation_id": "<CONVERSATION_ID>"
}
```

**Stop Typing:**
```json
{
  "type": "typing_stop",
  "conversation_id": "<CONVERSATION_ID>"
}
```

**Join Conversation:**
```json
{
  "type": "join_conversation",
  "conversation_id": "<CONVERSATION_ID>"
}
```

**Leave Conversation:**
```json
{
  "type": "leave_conversation",
  "conversation_id": "<CONVERSATION_ID>"
}
```

### Expected Server → Client Events

When another user sends a message, you should receive:
```json
{
  "type": "new_message",
  "conversation_id": "...",
  "message": {...}
}
```

When another user marks your message as read:
```json
{
  "type": "message_read",
  "message_id": "...",
  "read_by": "...",
  "read_at": "..."
}
```

---

## Troubleshooting

If requests hang or timeout:
1. Check server logs in the terminal
2. Verify server is running on port 8000
3. Check if database file exists: `beatspush.db`
4. Restart the server if needed
5. Check for error messages in console

---

## Next Steps After Manual Testing

Once manual testing confirms everything works:
1. Create automated integration tests
2. Add load testing
3. Test file upload functionality
4. Build frontend components
5. Test end-to-end with real WebSocket clients
