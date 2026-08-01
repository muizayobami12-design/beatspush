"""
API v1 Router - Combines all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, profiles, tracks, ai, campaigns, promo_links, analytics, tips, bookings, beats, social, messaging, websocket, fan_clubs, webhooks

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(profiles.router)
api_router.include_router(tracks.router)
api_router.include_router(ai.router)
api_router.include_router(campaigns.router)
api_router.include_router(promo_links.router)
api_router.include_router(analytics.router)
api_router.include_router(tips.router)
api_router.include_router(bookings.router)
api_router.include_router(beats.router)
api_router.include_router(social.router)
api_router.include_router(messaging.router)
api_router.include_router(websocket.router)
api_router.include_router(fan_clubs.router)
api_router.include_router(webhooks.router)

# Future routers will be added here:
# api_router.include_router(playlists.router)
# api_router.include_router(payments.router)
# etc.
