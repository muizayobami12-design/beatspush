# 📋 TASK 3.3: Social Media Integration - Implementation Guide

**Status:** 🔄 PENDING (External Dependencies Required)  
**Priority:** High (But requires setup first)  
**Estimated Time:** 2-3 weeks  
**Dependencies:** Developer accounts, API credentials, OAuth apps

---

## 🎯 Overview

Task 3.3 integrates Campaign Builder (Task 3.2) with actual social media platforms to enable real posting. Currently, campaigns generate and store content locally. This task makes them post to Instagram, Twitter, TikTok, and Facebook.

---

## 🚨 Prerequisites (MUST Complete First)

### 1. **Instagram Graph API**
**Requirements:**
- Facebook Developer Account
- Facebook App created
- Instagram Business Account
- App approved for Instagram Basic Display or Instagram Graph API
- Valid access tokens

**Setup Steps:**
1. Go to https://developers.facebook.com
2. Create new app (select "Business" type)
3. Add Instagram Graph API product
4. Configure OAuth redirect URIs
5. Submit for app review (if posting publicly)
6. Get App ID and App Secret

**Credentials Needed:**
```
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
INSTAGRAM_REDIRECT_URI=https://yourdomain.com/auth/instagram/callback
```

---

### 2. **Twitter/X API**
**Requirements:**
- Twitter Developer Account (https://developer.twitter.com)
- Elevated or Premium API access (Free tier very limited)
- OAuth 2.0 credentials
- API costs: ~$100/month for basic access

**Setup Steps:**
1. Apply for Twitter Developer Account
2. Create project and app
3. Enable OAuth 2.0
4. Get API keys and tokens
5. Set up callback URLs

**Credentials Needed:**
```
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

**Note:** Twitter API is now expensive. Consider if essential.

---

### 3. **TikTok API**
**Requirements:**
- TikTok Developer Account
- App registered on TikTok for Developers
- Business verification (for some features)
- Content Posting API access (requires approval)

**Setup Steps:**
1. Register at https://developers.tiktok.com
2. Create app
3. Apply for Content Posting API (requires approval process)
4. Wait 1-2 weeks for approval
5. Get Client Key and Client Secret

**Credentials Needed:**
```
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
```

**Warning:** TikTok API approval is strict. May require business documentation.

---

### 4. **Facebook API**
**Requirements:**
- Facebook Developer Account (same as Instagram)
- Facebook Page (for posting)
- Page access tokens
- Permissions: pages_manage_posts, pages_read_engagement

**Setup Steps:**
1. Use same Facebook app as Instagram
2. Add Facebook Login and Pages API products
3. Get Page ID and Page Access Token
4. Configure permissions

**Credentials Needed:**
```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token
```

---

## 📐 Technical Architecture

### **Database Changes Needed**

#### **social_accounts table** (NEW)
Store user's connected social media accounts:
```python
- id (UUID)
- user_id (FK to users)
- platform (instagram, twitter, tiktok, facebook)
- platform_user_id (external user ID)
- platform_username
- access_token (encrypted)
- refresh_token (encrypted)
- token_expires_at
- is_active
- connected_at
- last_sync_at
```

#### **post_attempts table** (NEW)
Track posting attempts and failures:
```python
- id (UUID)
- campaign_content_id (FK)
- social_account_id (FK)
- status (pending, success, failed)
- platform_post_id (external post ID)
- platform_post_url
- error_message
- attempted_at
- succeeded_at
```

---

## 🔐 OAuth Flow Implementation

### **Step 1: Connect Account**
```python
GET /api/v1/social/connect/{platform}
- Redirect to platform OAuth page
- User authorizes app
- Callback receives code
- Exchange code for tokens
- Store encrypted tokens in social_accounts
```

### **Step 2: Store Tokens Securely**
```python
from cryptography.fernet import Fernet

def encrypt_token(token: str) -> str:
    """Encrypt token before storage"""
    key = settings.ENCRYPTION_KEY
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    """Decrypt token for use"""
    key = settings.ENCRYPTION_KEY
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()
```

### **Step 3: Refresh Tokens**
```python
def refresh_access_token(social_account):
    """Refresh expired token"""
    if social_account.token_expires_at < now():
        # Call platform's token refresh endpoint
        # Update social_account with new token
        pass
```

---

## 🚀 Posting Implementation

### **Instagram Posting**
```python
def post_to_instagram(content: CampaignContent, social_account: SocialAccount):
    """Post to Instagram"""
    access_token = decrypt_token(social_account.access_token)
    
    # Upload image to Instagram
    # Create media container
    container = create_media_container(
        image_url=content.campaign.track.cover_art_url,
        caption=content.caption + " " + " ".join(content.hashtags),
        access_token=access_token
    )
    
    # Publish container
    result = publish_media_container(container.id, access_token)
    
    # Update content
    content.posting_status = "posted"
    content.posted_at = now()
    content.post_url = result.permalink
```

### **Twitter Posting**
```python
def post_to_twitter(content: CampaignContent, social_account: SocialAccount):
    """Post to Twitter/X"""
    import tweepy
    
    # Authenticate
    client = tweepy.Client(
        bearer_token=settings.TWITTER_BEARER_TOKEN,
        access_token=decrypt_token(social_account.access_token),
        access_token_secret=decrypt_token(social_account.access_secret)
    )
    
    # Post tweet
    tweet = client.create_tweet(
        text=content.caption[:280]  # Twitter limit
    )
    
    # Update content
    content.posting_status = "posted"
    content.posted_at = now()
    content.post_url = f"https://twitter.com/user/status/{tweet.data['id']}"
```

### **TikTok Posting**
```python
def post_to_tiktok(content: CampaignContent, social_account: SocialAccount):
    """Post to TikTok"""
    # Note: Requires video file, not just caption
    # May need to generate video from audio + cover art
    
    # Upload video
    # Add caption and hashtags
    # Publish
    pass
```

### **Facebook Posting**
```python
def post_to_facebook(content: CampaignContent, social_account: SocialAccount):
    """Post to Facebook Page"""
    import facebook
    
    graph = facebook.GraphAPI(decrypt_token(social_account.access_token))
    
    # Post to page
    post = graph.put_object(
        parent_object=social_account.platform_user_id,
        connection_name="feed",
        message=content.caption,
        link=f"https://beatpush.com/tracks/{content.campaign.track_id}"
    )
    
    # Update content
    content.posting_status = "posted"
    content.posted_at = now()
    content.post_url = f"https://facebook.com/{post['id']}"
```

---

## 📊 Analytics Integration

After posting, fetch engagement metrics:

```python
def sync_post_metrics(post_attempt: PostAttempt):
    """Fetch metrics from platform"""
    if post_attempt.platform == "instagram":
        metrics = fetch_instagram_metrics(post_attempt.platform_post_id)
        # Update campaign_content metrics
        content.engagement_count = metrics.likes + metrics.comments
        content.reach_count = metrics.reach
        content.shares_count = metrics.shares
```

---

## 🛠️ API Endpoints to Add

```python
# Social Account Management
POST   /api/v1/social/connect/{platform}        # Initiate OAuth
GET    /api/v1/social/callback/{platform}      # OAuth callback
GET    /api/v1/social/accounts                  # List connected accounts
DELETE /api/v1/social/accounts/{id}             # Disconnect account

# Posting
POST   /api/v1/campaigns/{id}/post              # Post to all platforms
POST   /api/v1/campaigns/{id}/post/{platform}   # Post to specific platform
GET    /api/v1/campaigns/{id}/post-status       # Check posting status

# Analytics
GET    /api/v1/campaigns/{id}/analytics         # Get real metrics
POST   /api/v1/social/sync-metrics              # Manually sync metrics
```

---

## ⚠️ Important Considerations

### **1. Rate Limits**
Each platform has different rate limits:
- Instagram: 200 requests/hour
- Twitter: Varies by tier ($$$)
- TikTok: Strict limits
- Facebook: 200 requests/hour

**Solution:** Implement rate limiting and queuing

---

### **2. Content Requirements**
Different platforms need different content:
- Instagram: Image (JPG/PNG) + caption
- Twitter: Text only or text + image
- TikTok: Video required (MP4)
- Facebook: Text, image, or link

**Solution:** Content adaptation layer

---

### **3. Webhook Handling**
Platforms send webhooks for:
- Post published
- Engagement updates
- Account disconnected
- Errors

**Solution:** Webhook receiver endpoints

---

### **4. Error Handling**
Common errors:
- Token expired
- Insufficient permissions
- Rate limit exceeded
- Content violates policies
- Account banned/restricted

**Solution:** Retry logic + user notifications

---

### **5. Compliance**
Must comply with:
- Platform Terms of Service
- Data privacy laws (GDPR, CCPA)
- Content policies
- API usage policies

---

## 📦 Dependencies to Install

```bash
pip install tweepy                    # Twitter
pip install facebook-sdk              # Facebook
pip install instagrapi               # Instagram (unofficial, more features)
pip install requests-oauthlib        # OAuth
pip install cryptography             # Token encryption
pip install celery                   # Background jobs
pip install redis                    # Queue backend
```

---

## 🚦 Implementation Phases

### **Phase 1: OAuth & Account Management** (1 week)
- Set up developer accounts
- Implement OAuth flow
- Store encrypted tokens
- Account connection UI

### **Phase 2: Instagram Integration** (3-4 days)
- Image posting
- Caption + hashtags
- Metrics fetching
- Error handling

### **Phase 3: Twitter Integration** (3-4 days)
- Tweet posting
- Media upload
- Engagement metrics

### **Phase 4: Facebook Integration** (2-3 days)
- Page posting
- Insights fetching

### **Phase 5: TikTok Integration** (1 week)
- Video generation from audio
- Video upload
- Caption overlay
- Analytics

### **Phase 6: Testing & Polish** (3-4 days)
- Error scenarios
- Rate limit handling
- Retry logic
- User notifications

**Total Time: 3-4 weeks**

---

## 💰 Cost Estimate

- Twitter API: $100/month (Basic tier)
- Server costs: $20/month (for background jobs)
- Development time: 3-4 weeks
- **Total Monthly:** ~$120

---

## ✅ Success Criteria

- [ ] Users can connect 4 social accounts
- [ ] OAuth flow works for all platforms
- [ ] Campaign publish posts to all connected accounts
- [ ] Posting status tracked per platform
- [ ] Errors handled gracefully with notifications
- [ ] Real metrics populate from platforms
- [ ] Rate limits respected
- [ ] Tokens refreshed automatically
- [ ] Secure token storage (encrypted)
- [ ] Webhooks receive updates

---

## 🎯 Why This Task is Deferred

1. **External Dependencies:** Requires developer accounts and API approvals
2. **API Costs:** Twitter charges $100/month minimum
3. **Approval Time:** TikTok can take 1-2 weeks
4. **Complexity:** OAuth, webhooks, rate limits require careful implementation
5. **Current Value:** Campaign Builder works without this (generates content)

**Recommendation:** Implement when ready to go to production and have:
- Developer accounts approved
- API credentials ready
- Budget for API costs
- Time for proper testing

---

## 📝 Current Workaround

For now, Campaign Builder:
- ✅ Generates AI content
- ✅ Stores content locally
- ✅ Shows "pending" posting status
- ✅ Has placeholder for metrics
- ✅ Structure ready for Task 3.3

Users can:
- Copy generated content
- Manually post to platforms
- Still benefit from AI generation and templates

---

## 🔮 Next Steps

**When ready to implement Task 3.3:**

1. Register developer accounts (2-3 days)
2. Get API credentials (1 week with approvals)
3. Read this document
4. Follow implementation phases
5. Test thoroughly
6. Deploy to production

**For now, proceed to:**
- ✅ Task 3.5: Promo Link Generator (no external dependencies)
- ✅ Phase 4: Analytics (can work independently)

---

**Document Created:** January 31, 2025  
**For:** Future implementation of social media posting  
**Status:** Ready for implementation when prerequisites are met
