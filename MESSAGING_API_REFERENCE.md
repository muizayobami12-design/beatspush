# Messaging System API Reference

## Quick Reference

### Authentication
All requests require JWT token:
```
Authorization: Bearer <jwt_token>
```

### Base URL
```
http://localhost:8000/api/v1/messaging
WebSocket: ws://localhost:8000/ws/conversations
```

---

## Endpoints

### Conversations

#### List Conversations
```
GET /conversations
```
**Query Parameters:**
- `page`: int (default: 1)
- `page_size`: int (default: 20, max: 100)
- `unread_only`: bool (filter to unread only)
- `search`: str (search by participant name)

**Response:**
```json
{
  "conversations": [
    {
      "id": "conv_123",
      "participants": [
        {
          "id": "user_1",
          "username": "alice",
          "full_name": "Alice",
          "avatar_url": "https://..."
        }
      ],
      "last_message": {
        "id": "msg_456",
        "content": "Hello!",
        "sender_id": "user_2",
        "created_at": "2024-09-02T11:26:37Z"
      },
      "unread_count": 0,
      "is_message_request": false,
      "request_status": "accepted",
      "last_activity_at": "2024-09-02T11:26:37Z",
      "is_archived": false,
      "is_muted": false
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

#### Create or Get Conversation
```
POST /conversations
Content-Type: application/json

{
  "recipient_id": "user_456"
}
```

**Response:** ConversationResponse (201 or 200 if exists)

#### Get Conversation Details
```
GET /conversations/{conversation_id}
```

**Response:** ConversationResponse (200)

#### Leave Conversation
```
DELETE /conversations/{conversation_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Left conversation"
}
```

---

### Messages

#### Get Messages in Conversation
```
GET /conversations/{conversation_id}/messages
```

**Query Parameters:**
- `page`: int (1-indexed)
- `page_size`: int (default: 50)
- `cursor`: str (cursor from last response)
- `before`: ISO8601 timestamp
- `after`: ISO8601 timestamp

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_123",
      "conversation_id": "conv_456",
      "sender_id": "user_789",
      "sender": {
        "id": "user_789",
        "username": "bob",
        "full_name": "Bob",
        "avatar_url": "https://..."
      },
      "content": "Hello Alice!",
      "created_at": "2024-09-02T11:26:37Z",
      "updated_at": "2024-09-02T11:26:37Z",
      "is_edited": false,
      "deleted_at": null,
      "read_by": [
        {
          "user_id": "user_1",
          "read_at": "2024-09-02T11:27:00Z"
        }
      ],
      "attachments": [
        {
          "id": "att_123",
          "file_type": "image",
          "original_filename": "photo.jpg",
          "storage_url": "https://r2.example.com/...",
          "file_size": 102400,
          "mime_type": "image/jpeg",
          "width": 1920,
          "height": 1080,
          "thumbnail_url": "https://r2.example.com/...thumb"
        }
      ]
    }
  ],
  "has_more": true,
  "next_cursor": "msg_abc123"
}
```

#### Send Message
```
POST /messages
Content-Type: application/json

{
  "recipient_id": "user_456",
  "conversation_id": "conv_789",  // OR recipient_id, not both required
  "content": "Hello!"
}
```

**Response:** MessageResponse (201)

**Status Codes:**
- 201: Message created
- 400: Bad request (blocked user, invalid content)
- 403: Forbidden (user not accepting messages)
- 404: Conversation not found

#### Edit Message
```
PUT /messages/{message_id}
Content-Type: application/json

{
  "content": "Hello! (edited)"
}
```

**Constraints:**
- Message must be from sender
- Must be within 15 minutes of creation
- Content: 1-2000 chars

**Response:** MessageResponse (200)

**Status Codes:**
- 200: Message updated
- 403: Not message sender
- 410: Too old to edit

#### Delete Message
```
DELETE /messages/{message_id}
```

**Behavior:**
- Soft delete (keeps history)
- Content replaced with "[Message deleted]"
- Read receipts preserved

**Response:**
```json
{
  "success": true,
  "message": "Message deleted"
}
```

#### Mark Message as Read
```
POST /messages/{message_id}/read
```

**Response:**
```json
{
  "success": true,
  "message": "Message marked as read"
}
```

#### Upload File Attachment
```
POST /messages/{message_id}/attachments
Content-Type: multipart/form-data

form-data:
  file: <binary>
  file_type: "image" | "audio" | "document" | "voice_note"
```

**File Limits:**
- Images: 10MB (jpg, png, gif, webp)
- Audio: 25MB (mp3, wav, m4a, ogg)
- Documents: 10MB (pdf, doc, docx)

**Response:** AttachmentResponse (201)

---

### Message Requests

#### List Pending Requests
```
GET /message-requests
```

**Query Parameters:**
- `page`: int (default: 1)
- `page_size`: int (default: 20)

**Response:** ConversationListResponse filtered to pending requests

#### Accept Message Request
```
POST /message-requests/{conversation_id}/accept
```

**Response:** ConversationResponse (200)

#### Decline Message Request
```
POST /message-requests/{conversation_id}/decline
```

**Response:**
```json
{
  "success": true,
  "message": "Request declined"
}
```

---

### Privacy & Settings

#### Get User Settings
```
GET /settings
```

**Response:**
```json
{
  "id": "setting_123",
  "user_id": "user_456",
  "message_filter": "everyone",
  "read_receipts_enabled": true,
  "typing_indicators_enabled": true
}
```

**Message Filter Values:**
- `everyone` - All users can message
- `followers` - Only followers can message
- `verified` - Only verified users can message
- `none` - No one can message (requests only)

#### Update User Settings
```
PUT /settings
Content-Type: application/json

{
  "message_filter": "followers",
  "read_receipts_enabled": false,
  "typing_indicators_enabled": true
}
```

**Response:** SettingsResponse (200)

#### Block User
```
POST /block
Content-Type: application/json

{
  "user_id": "user_to_block",
  "reason": "Spam"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "User blocked"
}
```

#### Unblock User
```
DELETE /block/{user_id}
```

**Response:**
```json
{
  "success": true,
  "message": "User unblocked"
}
```

#### Get Blocked Users
```
GET /blocked-users
```

**Query Parameters:**
- `page`: int (default: 1)
- `page_size`: int (default: 20)

**Response:**
```json
{
  "blocked_users": [
    {
      "id": "block_123",
      "user_id": "user_blocked",
      "username": "spammer",
      "full_name": "Spam User",
      "avatar_url": "https://...",
      "blocked_at": "2024-09-02T11:26:37Z",
      "reason": "Spam"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### Report Message
```
POST /messages/{message_id}/report
Content-Type: application/json

{
  "reason": "spam",  // "spam" | "harassment" | "inappropriate" | "other"
  "details": "This user keeps spamming me"  // optional, max 500 chars
}
```

**Response:**
```json
{
  "success": true,
  "message": "Report submitted"
}
```

---

### Polling Fallback

#### Poll for New Messages
```
GET /conversations/{conversation_id}/poll?since=2024-09-02T11:26:37Z
```

**Returns:**
- Messages since timestamp
- Typing indicator status
- Connected users in conversation

**Response:**
```json
{
  "messages": [ ],
  "typing_users": [
    {
      "user_id": "user_789",
      "username": "bob"
    }
  ],
  "online_users": ["user_1", "user_2"]
}
```

#### Get Unread Count
```
GET /unread-count
```

**Response:**
```json
{
  "unread_count": 5,
  "by_conversation": [
    {
      "conversation_id": "conv_123",
      "unread_count": 3
    },
    {
      "conversation_id": "conv_456",
      "unread_count": 2
    }
  ]
}
```

---

## WebSocket

### Connection
```
ws://localhost:8000/ws/conversations?token=<jwt_token>
```

### Incoming Events (Client → Server)

#### Join Conversation
```json
{
  "event": "join_conversation",
  "conversation_id": "conv_123"
}
```

#### Leave Conversation
```json
{
  "event": "leave_conversation",
  "conversation_id": "conv_123"
}
```

#### Start Typing
```json
{
  "event": "typing_start",
  "conversation_id": "conv_123"
}
```

#### Stop Typing
```json
{
  "event": "typing_stop",
  "conversation_id": "conv_123"
}
```

### Outgoing Events (Server → Client)

#### New Message
```json
{
  "event": "new_message",
  "data": {
    "id": "msg_123",
    "conversation_id": "conv_456",
    "sender": { },
    "content": "Hello!",
    "created_at": "2024-09-02T11:26:37Z"
  }
}
```

#### Message Deleted
```json
{
  "event": "message_deleted",
  "data": {
    "message_id": "msg_123",
    "conversation_id": "conv_456"
  }
}
```

#### Message Edited
```json
{
  "event": "message_edited",
  "data": {
    "message_id": "msg_123",
    "content": "Updated content",
    "updated_at": "2024-09-02T11:27:00Z"
  }
}
```

#### Typing Indicator
```json
{
  "event": "typing_indicator",
  "data": {
    "conversation_id": "conv_123",
    "user_id": "user_789",
    "username": "bob",
    "is_typing": true
  }
}
```

#### Read Receipt
```json
{
  "event": "message_read",
  "data": {
    "message_id": "msg_123",
    "user_id": "user_456",
    "read_at": "2024-09-02T11:27:00Z"
  }
}
```

#### User Online
```json
{
  "event": "user_online",
  "data": {
    "user_id": "user_789",
    "username": "bob",
    "timestamp": "2024-09-02T11:26:37Z"
  }
}
```

#### User Offline
```json
{
  "event": "user_offline",
  "data": {
    "user_id": "user_789",
    "username": "bob",
    "timestamp": "2024-09-02T11:26:37Z"
  }
}
```

---

## Error Codes

### Common HTTP Errors

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Invalid conversation ID format |
| 401 | Unauthorized | Missing or invalid JWT |
| 403 | Forbidden | User not in conversation / Blocked |
| 404 | Not Found | Conversation doesn't exist |
| 409 | Conflict | User already in conversation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Database connection failed |

### WebSocket Closure Codes

| Code | Meaning |
|------|---------|
| 1008 | Policy Violation (auth failed) |
| 1000 | Normal closure |
| 1006 | Abnormal closure |
| 1011 | Server error |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| POST /messages | 30/minute |
| POST /attachments | 10/minute |
| GET /conversations | 60/minute |
| POST /block | 10/minute |
| WebSocket messages | 60/minute |

**Response Headers:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1694254800
```

---

## Examples

### Send Message
```bash
curl -X POST http://localhost:8000/api/v1/messaging/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": "user_456",
    "content": "Hello Bob!"
  }'
```

### List Conversations
```bash
curl -X GET "http://localhost:8000/api/v1/messaging/conversations?page=1&unread_only=true" \
  -H "Authorization: Bearer $TOKEN"
```

### Upload File
```bash
curl -X POST http://localhost:8000/api/v1/messaging/messages/msg_123/attachments \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@photo.jpg" \
  -F "file_type=image"
```

### WebSocket Connect
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/conversations?token=' + jwtToken);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log('Event:', msg.event, msg.data);
};

// Send typing indicator
ws.send(JSON.stringify({
  event: 'typing_start',
  conversation_id: 'conv_123'
}));
```

---

## Troubleshooting

### 401 Unauthorized
- Check JWT token validity
- Verify token not expired
- Check `Authorization` header format

### 403 Forbidden
- User might be blocked
- Check recipient's message filter
- Verify user is conversation participant

### 429 Too Many Requests
- Wait before retrying
- Check rate limit headers
- Implement exponential backoff

### WebSocket Connection Failed
- Check WebSocket URL and token
- Verify CORS settings
- Check firewall rules
- Try polling fallback

---

## Support

For issues or questions about the Messaging API:
1. Check this documentation
2. Review error response details
3. Check backend logs
4. Contact support team

