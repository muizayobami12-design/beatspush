# Requirements Document

## Introduction

The Campaign Builder is a comprehensive promotional campaign management system for the BeatPush platform. It enables African music creators (Artists, DJs, Producers) to create, manage, and execute multi-platform promotional campaigns for their music tracks. The system integrates with the existing AI Content Generation Service (Task 3.1) to automate content creation and prepares campaigns for future social media integrations (Task 3.3). Campaigns generate and store platform-specific content locally without actual posting functionality at this stage.

## Glossary

- **Campaign_Builder**: The system component that manages the creation and lifecycle of promotional campaigns
- **Campaign**: A promotional initiative for a specific track, containing generated content for multiple social media platforms
- **AI_Service**: The existing AI Content Generation Service from Task 3.1 that provides 5 generation endpoints
- **Platform**: A social media service (Instagram, TikTok, Twitter, Facebook) targeted by the campaign
- **Campaign_Content**: AI-generated promotional materials (captions, hashtags, graphics) for specific platforms
- **Campaign_Template**: A predefined campaign structure with purpose-specific content strategies
- **Campaign_Status**: The current lifecycle state of a campaign (Draft, Scheduled, Active, Completed, Cancelled, Failed)
- **Creator**: A BeatPush user with role Artist, DJ, or Producer who can create campaigns
- **Track**: An uploaded music file in the BeatPush system that can be promoted via campaigns
- **Schedule**: A future date and time when a campaign should transition from Scheduled to Active status
- **Performance_Metrics**: Placeholder analytics data for campaign effectiveness (engagement, reach, clicks)

## Requirements

### Requirement 1: Campaign Creation

**User Story:** As a Creator, I want to create a promotional campaign for my track through a guided 5-step flow, so that I can efficiently generate multi-platform promotional content.

#### Acceptance Criteria

1. WHEN a Creator initiates campaign creation, THE Campaign_Builder SHALL display Step 1 for track selection
2. WHEN a Creator completes Step 1, THE Campaign_Builder SHALL display all tracks owned by the Creator with status "published"
3. WHEN a Creator selects a track in Step 1, THE Campaign_Builder SHALL advance to Step 2 for platform selection
4. WHEN a Creator views Step 2, THE Campaign_Builder SHALL display platform options: Instagram, TikTok, Twitter, Facebook
5. WHEN a Creator selects at least one platform in Step 2, THE Campaign_Builder SHALL enable advancement to Step 3
6. WHEN a Creator advances to Step 3, THE Campaign_Builder SHALL invoke the AI_Service to generate content for each selected platform
7. WHEN AI content generation completes, THE Campaign_Builder SHALL display generated content in Step 4 for review
8. WHEN a Creator edits content in Step 4, THE Campaign_Builder SHALL preserve the modifications
9. WHEN a Creator advances to Step 5, THE Campaign_Builder SHALL display options to publish immediately or schedule for future
10. WHEN a Creator completes Step 5 with immediate publish, THE Campaign_Builder SHALL create a campaign with status "Active"
11. WHEN a Creator completes Step 5 with scheduling, THE Campaign_Builder SHALL create a campaign with status "Scheduled"
12. WHEN a Creator creates a campaign, THE Campaign_Builder SHALL store the campaign with a unique identifier

### Requirement 2: Track Selection

**User Story:** As a Creator, I want to select from my published tracks when creating a campaign, so that I can promote the correct music.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL retrieve all tracks where user_id matches the Creator's id AND status equals "published"
2. WHEN displaying tracks for selection, THE Campaign_Builder SHALL show track title, artist name, cover art, and duration
3. WHEN a Creator searches tracks by title, THE Campaign_Builder SHALL filter the displayed tracks in real-time
4. WHEN a Creator selects a track, THE Campaign_Builder SHALL store the track_id in the campaign draft
5. IF a Creator has zero published tracks, THEN THE Campaign_Builder SHALL display a message directing them to upload tracks first
6. THE Campaign_Builder SHALL allow a Creator to change the selected track while in Step 1

### Requirement 3: Platform Selection

**User Story:** As a Creator, I want to choose which social media platforms to target, so that I can focus my promotional efforts effectively.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL display four platform options: Instagram, TikTok, Twitter, Facebook
2. WHEN a Creator selects a platform, THE Campaign_Builder SHALL visually indicate the selection
3. WHEN a Creator deselects a platform, THE Campaign_Builder SHALL remove the visual indication
4. THE Campaign_Builder SHALL allow selection of one or more platforms simultaneously
5. THE Campaign_Builder SHALL require selection of at least one platform before allowing advancement to Step 3
6. WHEN a Creator selects multiple platforms, THE Campaign_Builder SHALL store all selected platform identifiers in the campaign draft
7. THE Campaign_Builder SHALL allow a Creator to change platform selections while in Step 2

### Requirement 4: AI Content Generation

**User Story:** As a Creator, I want the system to automatically generate promotional content using AI, so that I can save time and get professional-quality marketing materials.

#### Acceptance Criteria

1. WHEN a Creator advances to Step 3, THE Campaign_Builder SHALL invoke AI_Service endpoint POST /api/v1/ai/generate-captions for each selected platform
2. WHEN generating captions, THE Campaign_Builder SHALL pass track_title, artist_name, genre, mood, and platform as parameters
3. WHEN a Creator advances to Step 3, THE Campaign_Builder SHALL invoke AI_Service endpoint POST /api/v1/ai/generate-hashtags with track_title, artist_name, genre, and location
4. WHEN AI_Service returns generated captions, THE Campaign_Builder SHALL store all caption variations with their tone labels
5. WHEN AI_Service returns generated hashtags, THE Campaign_Builder SHALL store hashtags categorized by genre, trending, location, and campaign
6. IF AI_Service endpoint returns an error, THEN THE Campaign_Builder SHALL display an error message and allow retry
7. WHILE AI content is generating, THE Campaign_Builder SHALL display a loading indicator
8. WHEN all AI generation completes successfully, THE Campaign_Builder SHALL automatically advance to Step 4
9. THE Campaign_Builder SHALL generate content specific to each selected platform's format and character limits

### Requirement 5: Content Review and Customization

**User Story:** As a Creator, I want to review and edit AI-generated content before finalizing the campaign, so that I can ensure the messaging aligns with my brand voice.

#### Acceptance Criteria

1. WHEN a Creator enters Step 4, THE Campaign_Builder SHALL display all generated content organized by platform
2. THE Campaign_Builder SHALL display caption variations with their tone labels for each platform
3. THE Campaign_Builder SHALL allow a Creator to select one caption variation per platform as the primary caption
4. WHEN a Creator edits a caption, THE Campaign_Builder SHALL update the stored content in real-time
5. THE Campaign_Builder SHALL display all generated hashtags categorized by type
6. WHEN a Creator removes a hashtag, THE Campaign_Builder SHALL update the stored hashtag list
7. WHEN a Creator adds a custom hashtag, THE Campaign_Builder SHALL append it to the campaign hashtag list
8. THE Campaign_Builder SHALL enforce platform-specific character limits when editing captions
9. THE Campaign_Builder SHALL provide a preview of how the content will appear on each platform
10. THE Campaign_Builder SHALL allow a Creator to return to previous steps to modify track or platform selections

### Requirement 6: Campaign Scheduling and Publishing

**User Story:** As a Creator, I want to either publish my campaign immediately or schedule it for a future date, so that I can control when my promotional content becomes active.

#### Acceptance Criteria

1. WHEN a Creator enters Step 5, THE Campaign_Builder SHALL display two options: "Publish Now" and "Schedule for Later"
2. WHEN a Creator selects "Publish Now", THE Campaign_Builder SHALL create the campaign with status "Active" and set published_at to the current timestamp
3. WHEN a Creator selects "Schedule for Later", THE Campaign_Builder SHALL display a date and time picker
4. WHEN a Creator selects a scheduled date, THE Campaign_Builder SHALL validate that the date is in the future
5. IF the scheduled date is not in the future, THEN THE Campaign_Builder SHALL display an error message
6. WHEN a Creator confirms scheduling, THE Campaign_Builder SHALL create the campaign with status "Scheduled" and store the scheduled_publish_time
7. THE Campaign_Builder SHALL display a confirmation message showing the campaign name and publication status
8. WHEN a campaign is created, THE Campaign_Builder SHALL assign a unique campaign_id
9. WHEN a campaign is created, THE Campaign_Builder SHALL set created_at to the current timestamp

### Requirement 7: Campaign Dashboard

**User Story:** As a Creator, I want to view all my campaigns organized by status, so that I can manage my promotional activities effectively.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL provide a dashboard displaying all campaigns owned by the Creator
2. THE Campaign_Builder SHALL organize campaigns into tabs: "Active", "Scheduled", "Past", "All"
3. WHEN a Creator selects the "Active" tab, THE Campaign_Builder SHALL display campaigns with status "Active"
4. WHEN a Creator selects the "Scheduled" tab, THE Campaign_Builder SHALL display campaigns with status "Scheduled" ordered by scheduled_publish_time ascending
5. WHEN a Creator selects the "Past" tab, THE Campaign_Builder SHALL display campaigns with status "Completed" or "Cancelled" ordered by completed_at descending
6. WHEN a Creator selects the "All" tab, THE Campaign_Builder SHALL display all campaigns ordered by created_at descending
7. THE Campaign_Builder SHALL display campaign cards showing campaign name, track title, selected platforms, status, and creation date
8. WHEN a Creator clicks a campaign card, THE Campaign_Builder SHALL navigate to the campaign detail view
9. THE Campaign_Builder SHALL display placeholder performance metrics on campaign cards (engagement, reach, clicks)
10. IF a Creator has zero campaigns, THEN THE Campaign_Builder SHALL display a message encouraging them to create their first campaign

### Requirement 8: Campaign Detail View

**User Story:** As a Creator, I want to view detailed information about a specific campaign, so that I can review the content and monitor its status.

#### Acceptance Criteria

1. WHEN a Creator opens a campaign detail view, THE Campaign_Builder SHALL display the campaign name, track title, and current status
2. THE Campaign_Builder SHALL display all platforms targeted by the campaign
3. THE Campaign_Builder SHALL display the selected caption for each platform
4. THE Campaign_Builder SHALL display all hashtags used in the campaign
5. THE Campaign_Builder SHALL display the scheduled_publish_time if status is "Scheduled"
6. THE Campaign_Builder SHALL display the published_at timestamp if status is "Active" or "Completed"
7. THE Campaign_Builder SHALL display placeholder performance metrics organized by platform
8. WHEN a campaign status is "Scheduled", THE Campaign_Builder SHALL display an "Edit" button
9. WHEN a campaign status is "Active", THE Campaign_Builder SHALL display a "Cancel" button
10. THE Campaign_Builder SHALL display a "Delete" button for campaigns with status "Draft", "Cancelled", or "Completed"

### Requirement 9: Campaign Templates

**User Story:** As a Creator, I want to use predefined campaign templates, so that I can quickly create campaigns optimized for specific promotional goals.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL provide six campaign templates: "New Release", "Pre-Release Teaser", "Behind The Scenes", "Fan Engagement", "Milestone Celebration", "Throwback Thursday"
2. WHEN a Creator starts campaign creation, THE Campaign_Builder SHALL display an optional template selection screen
3. WHEN a Creator selects a template, THE Campaign_Builder SHALL apply template-specific content strategy to AI generation prompts
4. WHEN "New Release" template is selected, THE Campaign_Builder SHALL configure AI prompts to emphasize excitement and availability
5. WHEN "Pre-Release Teaser" template is selected, THE Campaign_Builder SHALL configure AI prompts to build anticipation and mystery
6. WHEN "Behind The Scenes" template is selected, THE Campaign_Builder SHALL configure AI prompts to focus on creative process and authenticity
7. WHEN "Fan Engagement" template is selected, THE Campaign_Builder SHALL configure AI prompts to encourage interaction and questions
8. WHEN "Milestone Celebration" template is selected, THE Campaign_Builder SHALL configure AI prompts to highlight achievements and gratitude
9. WHEN "Throwback Thursday" template is selected, THE Campaign_Builder SHALL configure AI prompts to create nostalgic content about older tracks
10. THE Campaign_Builder SHALL store the selected template_id with the campaign
11. THE Campaign_Builder SHALL allow a Creator to skip template selection and create a custom campaign

### Requirement 10: Campaign Lifecycle Management

**User Story:** As a Creator, I want campaigns to automatically transition between statuses, so that my scheduled campaigns become active at the right time.

#### Acceptance Criteria

1. WHEN a campaign is created with status "Scheduled", THE Campaign_Builder SHALL store the scheduled_publish_time
2. WHEN the current time equals or exceeds a campaign's scheduled_publish_time, THE Campaign_Builder SHALL update the campaign status from "Scheduled" to "Active"
3. WHEN a campaign status changes to "Active", THE Campaign_Builder SHALL set the published_at timestamp to the current time
4. THE Campaign_Builder SHALL check for scheduled campaigns eligible for activation every 5 minutes
5. WHEN a Creator manually cancels an "Active" campaign, THE Campaign_Builder SHALL update the status to "Cancelled" and set cancelled_at timestamp
6. WHEN a Creator manually cancels a "Scheduled" campaign, THE Campaign_Builder SHALL update the status to "Cancelled" and set cancelled_at timestamp
7. THE Campaign_Builder SHALL allow manual transition from "Active" to "Completed" status with completed_at timestamp
8. THE Campaign_Builder SHALL prevent status transitions from "Completed" or "Cancelled" to any other status
9. WHEN a status transition fails, THE Campaign_Builder SHALL update the status to "Failed" and log the error_message

### Requirement 11: Campaign Editing

**User Story:** As a Creator, I want to edit scheduled campaigns, so that I can adjust content or timing before the campaign becomes active.

#### Acceptance Criteria

1. WHEN a campaign status is "Scheduled", THE Campaign_Builder SHALL allow the Creator to edit the campaign
2. WHEN editing a scheduled campaign, THE Campaign_Builder SHALL allow modification of captions for each platform
3. WHEN editing a scheduled campaign, THE Campaign_Builder SHALL allow addition or removal of hashtags
4. WHEN editing a scheduled campaign, THE Campaign_Builder SHALL allow modification of the scheduled_publish_time
5. WHEN editing a scheduled campaign, THE Campaign_Builder SHALL allow addition or removal of platforms
6. IF a Creator adds a platform during editing, THEN THE Campaign_Builder SHALL invoke AI_Service to generate content for the new platform
7. WHEN a Creator saves campaign edits, THE Campaign_Builder SHALL update the updated_at timestamp
8. THE Campaign_Builder SHALL prevent editing of campaigns with status "Active", "Completed", "Cancelled", or "Failed"
9. THE Campaign_Builder SHALL display a message when attempting to edit non-editable campaigns

### Requirement 12: Campaign Deletion

**User Story:** As a Creator, I want to delete campaigns that are no longer needed, so that I can keep my dashboard organized.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL allow deletion of campaigns with status "Draft", "Cancelled", or "Completed"
2. WHEN a Creator initiates campaign deletion, THE Campaign_Builder SHALL display a confirmation dialog
3. WHEN a Creator confirms deletion, THE Campaign_Builder SHALL remove the campaign and all associated content from the database
4. THE Campaign_Builder SHALL prevent deletion of campaigns with status "Active" or "Scheduled"
5. IF a Creator attempts to delete a non-deletable campaign, THEN THE Campaign_Builder SHALL display an error message
6. WHEN a campaign is deleted, THE Campaign_Builder SHALL remove the campaign from the dashboard view
7. THE Campaign_Builder SHALL log campaign deletions for audit purposes

### Requirement 13: Performance Metrics Placeholders

**User Story:** As a Creator, I want to see placeholder performance metrics for my campaigns, so that I understand what analytics will be available when social media integrations are complete.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL display placeholder metrics for each campaign: engagement_count, reach_count, clicks_count, shares_count
2. THE Campaign_Builder SHALL initialize all placeholder metrics to zero when a campaign is created
3. THE Campaign_Builder SHALL display metrics broken down by platform
4. THE Campaign_Builder SHALL allow manual entry of metric values for testing purposes
5. THE Campaign_Builder SHALL display metrics in a visually organized dashboard format
6. THE Campaign_Builder SHALL show metrics as "Not yet available - Coming with Social Media Integration (Task 3.3)" label
7. THE Campaign_Builder SHALL prepare the database schema to store real metrics when social media APIs are integrated

### Requirement 14: Multi-Platform Content Storage

**User Story:** As a Creator, I want all generated campaign content to be stored locally in the database, so that it is ready for future social media posting integrations.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL store campaign content in a structured format organized by platform
2. WHEN storing Instagram content, THE Campaign_Builder SHALL store caption, hashtags, and content_type (feed/story/reel)
3. WHEN storing TikTok content, THE Campaign_Builder SHALL store caption, hashtags, and video_idea_description
4. WHEN storing Twitter content, THE Campaign_Builder SHALL store tweet_text, hashtags, and thread_indicator
5. WHEN storing Facebook content, THE Campaign_Builder SHALL store post_text, hashtags, and post_type (status/photo/video)
6. THE Campaign_Builder SHALL store each platform's content as a separate record linked to the campaign_id
7. THE Campaign_Builder SHALL store content_generated_at timestamp for each platform's content
8. THE Campaign_Builder SHALL store content_edited flag to track manual modifications
9. THE Campaign_Builder SHALL preserve original AI-generated content separately from edited versions
10. THE Campaign_Builder SHALL prepare content fields to accept posting_status values when Task 3.3 is implemented

### Requirement 15: Campaign Search and Filtering

**User Story:** As a Creator, I want to search and filter my campaigns, so that I can quickly find specific promotional initiatives.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL provide a search input on the campaign dashboard
2. WHEN a Creator enters search text, THE Campaign_Builder SHALL filter campaigns by campaign name or track title
3. THE Campaign_Builder SHALL provide filter options for campaign status
4. THE Campaign_Builder SHALL provide filter options for platforms
5. WHEN a Creator selects a status filter, THE Campaign_Builder SHALL display only campaigns matching that status
6. WHEN a Creator selects a platform filter, THE Campaign_Builder SHALL display only campaigns targeting that platform
7. THE Campaign_Builder SHALL allow multiple filters to be applied simultaneously
8. THE Campaign_Builder SHALL display the count of campaigns matching current filters
9. THE Campaign_Builder SHALL provide a "Clear Filters" action to reset all filters
10. THE Campaign_Builder SHALL persist search and filter selections while navigating within the dashboard

### Requirement 16: Campaign Duplication

**User Story:** As a Creator, I want to duplicate existing campaigns, so that I can quickly create similar promotional campaigns for different tracks.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL provide a "Duplicate" action on campaign detail views for campaigns with status "Completed" or "Active"
2. WHEN a Creator duplicates a campaign, THE Campaign_Builder SHALL create a new campaign with status "Draft"
3. WHEN duplicating, THE Campaign_Builder SHALL copy the platform selections from the original campaign
4. WHEN duplicating, THE Campaign_Builder SHALL copy the template selection from the original campaign
5. WHEN duplicating, THE Campaign_Builder SHALL NOT copy the track selection (Creator must select a new track)
6. WHEN duplicating, THE Campaign_Builder SHALL NOT copy the generated content (new content must be generated)
7. WHEN duplicating, THE Campaign_Builder SHALL create a new campaign_id
8. WHEN duplicating, THE Campaign_Builder SHALL append " (Copy)" to the campaign name
9. WHEN duplicating completes, THE Campaign_Builder SHALL navigate the Creator to Step 1 of the campaign creation flow with saved platform and template selections

### Requirement 17: User Role Restrictions

**User Story:** As a system administrator, I want campaign creation restricted to Creator roles, so that only appropriate users can create promotional campaigns.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL allow campaign creation only for users with role "artist", "dj", or "producer"
2. IF a user with role "fan" or "admin" attempts to access campaign creation, THEN THE Campaign_Builder SHALL display an error message
3. THE Campaign_Builder SHALL validate user role before displaying the campaign creation flow
4. THE Campaign_Builder SHALL validate user role before processing campaign creation API requests
5. THE Campaign_Builder SHALL display campaigns only to the Creator who created them
6. THE Campaign_Builder SHALL prevent users from viewing or editing campaigns created by other users
7. IF a user role is "admin", THEN THE Campaign_Builder SHALL allow viewing all campaigns for moderation purposes

### Requirement 18: Campaign Name Generation

**User Story:** As a Creator, I want campaigns to have automatically generated names, so that I can easily identify them without manual naming effort.

#### Acceptance Criteria

1. WHEN a campaign is created, THE Campaign_Builder SHALL generate a campaign name using the format: "{Template_Name} - {Track_Title}"
2. IF no template was selected, THEN THE Campaign_Builder SHALL generate a campaign name using the format: "Campaign - {Track_Title}"
3. WHEN a campaign name exceeds 100 characters, THE Campaign_Builder SHALL truncate the track_title portion and append "..."
4. THE Campaign_Builder SHALL allow a Creator to edit the generated campaign name before finalizing creation
5. THE Campaign_Builder SHALL validate that campaign names are unique per Creator
6. IF a campaign name already exists for the Creator, THEN THE Campaign_Builder SHALL append a numeric suffix (e.g., " (2)", " (3)")

### Requirement 19: AI Service Error Handling

**User Story:** As a Creator, I want clear error messages when AI content generation fails, so that I understand what went wrong and can take corrective action.

#### Acceptance Criteria

1. WHEN AI_Service returns a 503 error, THE Campaign_Builder SHALL display "AI service is temporarily unavailable. Please try again in a few moments."
2. WHEN AI_Service returns a 500 error, THE Campaign_Builder SHALL display "Content generation failed. Please try again."
3. WHEN AI_Service request times out, THE Campaign_Builder SHALL display "Content generation is taking longer than expected. Please try again."
4. THE Campaign_Builder SHALL provide a "Retry Generation" button when AI generation fails
5. WHEN a Creator clicks "Retry Generation", THE Campaign_Builder SHALL re-invoke the failed AI_Service endpoints
6. THE Campaign_Builder SHALL log all AI_Service errors with timestamp and request parameters for debugging
7. WHEN multiple AI_Service endpoints fail, THE Campaign_Builder SHALL display the count of failed generations
8. THE Campaign_Builder SHALL allow a Creator to proceed with partial content if some AI generations succeed
9. IF all AI generations fail, THEN THE Campaign_Builder SHALL prevent advancement to Step 4

### Requirement 20: Campaign Activity Logging

**User Story:** As a system administrator, I want all campaign actions logged, so that I can audit campaign usage and troubleshoot issues.

#### Acceptance Criteria

1. THE Campaign_Builder SHALL log campaign creation events with creator_id, campaign_id, track_id, and timestamp
2. THE Campaign_Builder SHALL log campaign status transitions with old_status, new_status, campaign_id, and timestamp
3. THE Campaign_Builder SHALL log campaign edits with campaign_id, modified_fields, and timestamp
4. THE Campaign_Builder SHALL log campaign deletions with campaign_id, deleted_by_user_id, and timestamp
5. THE Campaign_Builder SHALL log AI_Service invocations with endpoint, parameters, response_status, and timestamp
6. THE Campaign_Builder SHALL log campaign duplication events with source_campaign_id, new_campaign_id, and timestamp
7. THE Campaign_Builder SHALL store logs in a dedicated campaign_activity_log table
8. THE Campaign_Builder SHALL retain activity logs for 90 days minimum
9. THE Campaign_Builder SHALL provide log export functionality for administrators
