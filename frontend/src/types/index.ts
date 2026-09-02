/**
 * Core type definitions for the BeatPush application
 */

export type UserRole = 'artist' | 'dj' | 'producer' | 'fan' | 'admin';

export interface User {
  id: string;
  email: string;
  fullName: string;
  username?: string;
  role: UserRole;
  avatar?: string;
  coverPhoto?: string;
  bio?: string;
  location?: string;
  socialLinks?: SocialLinks;
  isVerified: boolean;
  followerCount: number;
  followingCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface SocialLinks {
  spotify?: string;
  appleMusic?: string;
  instagram?: string;
  twitter?: string;
  facebook?: string;
  tiktok?: string;
}

export interface Profile extends Omit<User, 'followerCount' | 'followingCount'> {
  username: string;
  stageName?: string;
  genres?: string[];
  recordLabel?: string;
  equipment?: string;
  availableForBooking?: boolean;
  bookingRate?: number;
  website?: string;
  isFollowing?: boolean;
  followersCount?: number;
  followingCount?: number;
  beatsCount?: number;
  avatarUrl?: string;
  coverPhotoUrl?: string;
}

export interface Beat {
  id: string;
  title: string;
  creatorId: string;
  creator: User;
  audioUrl: string;
  waveformUrl?: string;
  thumbnailUrl?: string;
  genre: string;
  tempo: number;
  key: string;
  duration: number;
  price: number;
  licenses?: LicenseOption[];
  tags: string[];
  playCount: number;
  favoriteCount: number;
  isFavorited?: boolean;
  isPurchased?: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface LicenseOption {
  id: string;
  name: string;
  price: number;
  description: string;
  usageRights: string[];
}

export interface BeatFilters {
  search?: string;
  genre?: string[];
  tempoMin?: number;
  tempoMax?: number;
  priceMin?: number;
  priceMax?: number;
  key?: string;
  sortBy?: 'newest' | 'popular' | 'price_asc' | 'price_desc';
}

export interface Message {
  id: string;
  conversationId: string;
  senderId: string;
  sender: User;
  content: string;
  status: 'sent' | 'delivered' | 'read';
  createdAt: string;
}

export interface Conversation {
  id: string;
  participants: User[];
  lastMessage?: Message;
  unreadCount: number;
  updatedAt: string;
}

export interface Campaign {
  id: string;
  userId: string;
  title: string;
  description: string;
  targetContentId: string;
  targetContentType: 'track' | 'beat';
  budget: number;
  spent: number;
  startDate: string;
  endDate: string;
  status: 'draft' | 'scheduled' | 'active' | 'paused' | 'completed';
  metrics?: CampaignMetrics;
  createdAt: string;
  updatedAt: string;
}

export interface CampaignMetrics {
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number;
  costPerConversion: number;
}

export interface Post {
  id: string;
  user: User;
  postType: 'status' | 'track_share' | 'event' | 'milestone' | 'poll';
  content: string;
  mediaUrl?: string;
  track?: TrackBasic;
  eventDate?: string;
  pollOptions?: string[];
  pollEndsAt?: string;
  likeCount: number;
  commentCount: number;
  shareCount: number;
  isLiked?: boolean;
  isBookmarked?: boolean;
  visibility: 'public' | 'followers' | 'private';
  isPinned: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface TrackBasic {
  id: string;
  title: string;
  artistName: string;
  coverArtUrl?: string;
}

export interface Comment {
  id: string;
  postId: string;
  user: User;
  parentCommentId?: string;
  content: string;
  likeCount: number;
  isEdited: boolean;
  createdAt: string;
  updatedAt: string;
  replies?: Comment[];
}

export interface Notification {
  id: string;
  userId: string;
  type:
    | 'follow'
    | 'like'
    | 'comment'
    | 'message'
    | 'booking'
    | 'payment'
    | 'system';
  actorId?: string;
  actor?: User;
  targetId?: string;
  targetType?: 'post' | 'beat' | 'track' | 'comment';
  content: string;
  isRead: boolean;
  createdAt: string;
}

export interface AnalyticsOverview {
  totalPlays: number;
  totalLikes: number;
  totalShares: number;
  revenue: number;
  playsDelta: number;
  likesDelta: number;
  sharesDelta: number;
  revenueDelta: number;
}

export interface TimeSeriesData {
  date: string;
  value: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface APIResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}
