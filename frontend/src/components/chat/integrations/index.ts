/**
 * AI Chat Integrations
 * Export all page-specific integrations
 */

export {
  ProfileIntegration,
  useProfileChat,
  type ProfileIntegrationProps,
} from './ProfileIntegration';

export {
  SocialMediaIntegration,
  SocialMediaExample,
  useSocialMediaAI,
  extractSocialMediaContext,
  type SocialMediaIntegrationProps,
} from './SocialMediaIntegration';

export {
  BeatUploadIntegration,
  useBeatUploadAI,
  type BeatUploadIntegrationProps,
} from './BeatUploadIntegration';

export {
  CampaignIntegration,
  useCampaignAI,
  type CampaignIntegrationProps,
} from './CampaignIntegration';

export {
  AnalyticsIntegration,
  useAnalyticsAI,
  type AnalyticsIntegrationProps,
} from './AnalyticsIntegration';
