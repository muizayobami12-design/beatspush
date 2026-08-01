# Task List: Campaign Builder Implementation

## Task 1: Database Models and Migrations
**Priority:** High  
**Estimated Time:** 3 hours  
**Dependencies:** None

Create all database models for the Campaign Builder feature.

### Sub-tasks:
1.1. Create `app/models/campaign.py` with all enum types and model classes
    - CampaignStatus enum (DRAFT, SCHEDULED, ACTIVE, COMPLETED, CANCELLED, FAILED)
    - Platform enum (INSTAGRAM, TIKTOK, TWITTER, FACEBOOK)
    - ContentType enum (all platform-specific types)
    - Campaign model with all fields and relationships
    - CampaignContent model with all fields and relationships
    - CampaignTemplate model with all fields
    - CampaignActivityLog model with all fields

1.2. Update `app/models/__init__.py` to export new models

1.3. Create Alembic migration for new tables
    - Run `alembic revision --autogenerate -m "Add campaign tables"`
    - Review generated migration
    - Apply migration with `alembic upgrade head`

1.4. Verify tables created in database
    - Run `python check_db.py` to confirm new tables
    - Verify indexes are created
    - Verify foreign key constraints

**Acceptance Criteria:**
- All 4 tables exist in database
- All indexes are created
- Foreign key relationships work correctly
- Models can be imported successfully

---

## Task 2: Campaign Template Seed Data
**Priority:** High  
**Estimated Time:** 1 hour  
**Dependencies:** Task 1

Create seed data for the 6 campaign templates.

### Sub-tasks:
2.1. Create `backend/seed_campaign_templates.py` script
    - Define all 6 templates with prompts strategies
    - New Release template
    - Pre-Release Teaser template
    - Behind The Scenes template
    - Fan Engagement template
    - Milestone Celebration template
    - Throwback Thursday template

2.2. Run seed script to populate templates

2.3. Verify templates in database

**Acceptance Criteria:**
- 6 templates exist in campaign_templates table
- Each template has proper prompt_strategy JSON
- Each template has recommended_platforms
- Templates can be queried successfully

---

## Task 3: Pydantic Schemas
**Priority:** High  
**Estimated Time:** 2 hours  
**Dependencies:** Task 1

Create all request and response schemas for the Campaign Builder.

### Sub-tasks:
3.1. Create `app/schemas/campaign.py` with all schemas
    - CampaignCreateRequest
    - CampaignUpdateRequest
    - CampaignScheduleRequest (with future time validator)
    - ContentGenerateRequest
    - ContentUpdateRequest
    - CampaignContentResponse
    - CampaignResponse
    - CampaignDetailResponse
    - CampaignListResponse
    - CampaignTemplateResponse
    - CampaignTemplateListResponse
    - MessageResponse (if not already exists)

3.2. Add validation rules
    - Future time validator for scheduling
    - Platform name validation
    - Character limit hints in docstrings

3.3. Update `app/schemas/__init__.py` to export schemas

**Acceptance Criteria:**
- All schemas defined with proper types
- Validation works correctly
- from_attributes=True set for ORM models
- Schemas can be imported and used

---

## Task 4: Campaign Service Layer
**Priority:** High  
**Estimated Time:** 5 hours  
**Dependencies:** Task 1, Task 2, Task 3

Implement the CampaignService with all business logic.

### Sub-tasks:
4.1. Create `app/services/campaign_service.py`
    - CampaignService class with all static methods

4.2. Implement campaign management methods:
    - create_campaign() - Create new campaign
    - update_campaign() - Update campaign details
    - delete_campaign() - Delete campaign
    - duplicate_campaign() - Duplicate existing campaign
    - get_user_campaigns() - Get filtered campaign list
    - get_campaign_by_id() - Get single campaign

4.3. Implement content generation methods:
    - generate_content() - Generate AI content for platforms
    - update_content() - Update platform-specific content
    - Integration with AIService from Task 3.1

4.4. Implement workflow methods:
    - schedule_campaign() - Schedule for future
    - publish_campaign() - Publish immediately
    - cancel_campaign() - Cancel active/scheduled
    - complete_campaign() - Mark as completed

4.5. Implement utility methods:
    - generate_campaign_name() - Auto-generate names
    - log_activity() - Log all campaign actions
    - validate_campaign_ownership() - Authorization check
    - can_edit_campaign() - Check if editable
    - can_delete_campaign() - Check if deletable

4.6. Add error handling and validation
    - Validate track ownership
    - Validate status transitions
    - Handle AI service errors
    - Log all errors

**Acceptance Criteria:**
- All methods implemented and working
- Proper error handling
- Activity logging works
- AI service integration functional
- Status transitions follow rules

---

## Task 5: Campaign API Endpoints
**Priority:** High  
**Estimated Time:** 4 hours  
**Dependencies:** Task 4

Create all REST API endpoints for campaigns.

### Sub-tasks:
5.1. Create `app/api/v1/endpoints/campaigns.py`
    - Setup router with prefix="/campaigns"

5.2. Implement campaign management endpoints:
    - POST /campaigns - Create campaign
    - GET /campaigns - List campaigns with filters
    - GET /campaigns/{campaign_id} - Get campaign details
    - PUT /campaigns/{campaign_id} - Update campaign
    - DELETE /campaigns/{campaign_id} - Delete campaign

5.3. Implement campaign action endpoints:
    - POST /campaigns/{campaign_id}/duplicate - Duplicate
    - POST /campaigns/{campaign_id}/cancel - Cancel
    - POST /campaigns/{campaign_id}/complete - Mark complete
    - POST /campaigns/{campaign_id}/schedule - Schedule
    - POST /campaigns/{campaign_id}/publish - Publish now

5.4. Implement content endpoints:
    - POST /campaigns/{campaign_id}/generate-content - Generate AI content
    - GET /campaigns/{campaign_id}/content - Get all content
    - PUT /campaigns/{campaign_id}/content/{platform} - Update content

5.5. Implement template endpoints:
    - GET /campaign-templates - List templates
    - GET /campaign-templates/{template_id} - Get template

5.6. Add authentication and authorization:
    - Require JWT token for all endpoints
    - Verify user owns campaign
    - Check user role (Artist, DJ, Producer only)

5.7. Add comprehensive API documentation
    - Docstrings for all endpoints
    - Request/response examples
    - Error code documentation

**Acceptance Criteria:**
- All 15 endpoints implemented
- Authentication required
- Authorization checks work
- Proper HTTP status codes
- API documentation complete

---

## Task 6: Router Registration
**Priority:** High  
**Estimated Time:** 30 minutes  
**Dependencies:** Task 5

Register campaign router in the main API.

### Sub-tasks:
6.1. Update `app/api/v1/api.py`
    - Import campaigns router
    - Include router in api_router
    - Verify prefix and tags

6.2. Test router registration
    - Restart server
    - Check /openapi.json for new endpoints
    - Verify endpoints accessible

**Acceptance Criteria:**
- Campaign router registered
- All endpoints visible in OpenAPI
- No import errors
- Server starts successfully

---

## Task 7: Background Task - Campaign Scheduler
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Dependencies:** Task 4

Create background task to activate scheduled campaigns.

### Sub-tasks:
7.1. Create `app/tasks/campaign_scheduler.py`
    - activate_scheduled_campaigns() function
    - Query SCHEDULED campaigns with past scheduled_publish_time
    - Call CampaignService.publish_campaign() for each
    - Handle errors and set FAILED status

7.2. Create scheduler runner script
    - `backend/run_campaign_scheduler.py`
    - Use Python `schedule` library or similar
    - Run every 5 minutes
    - Add logging

7.3. Document how to run scheduler
    - Add to README or separate doc
    - Systemd service example (Linux)
    - Windows Task Scheduler example
    - Docker/PM2 examples

**Acceptance Criteria:**
- Scheduler function works correctly
- Scheduled campaigns activate on time
- Errors handled gracefully
- Logging implemented
- Documentation complete

---

## Task 8: Unit Tests - Models
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Dependencies:** Task 1

Create unit tests for campaign models.

### Sub-tasks:
8.1. Create `backend/tests/test_campaign_models.py`
    - Test Campaign model creation
    - Test CampaignContent model creation
    - Test relationships
    - Test enum values
    - Test default values

**Acceptance Criteria:**
- All model tests pass
- Relationships tested
- Enums work correctly
- Default values set properly

---

## Task 9: Unit Tests - Service Layer
**Priority:** Medium  
**Estimated Time:** 3 hours  
**Dependencies:** Task 4

Create unit tests for CampaignService.

### Sub-tasks:
9.1. Create `backend/tests/test_campaign_service.py`
    - Test create_campaign()
    - Test generate_content() with mocked AIService
    - Test update_campaign()
    - Test schedule_campaign()
    - Test publish_campaign()
    - Test cancel_campaign()
    - Test delete_campaign()
    - Test duplicate_campaign()
    - Test status transition validations
    - Test authorization checks

**Acceptance Criteria:**
- All service methods tested
- AI service mocked properly
- Status transitions verified
- Error cases tested
- Authorization tests pass

---

## Task 10: Integration Tests - API Endpoints
**Priority:** Medium  
**Estimated Time:** 4 hours  
**Dependencies:** Task 5

Create integration tests for all campaign endpoints.

### Sub-tasks:
10.1. Create `backend/test_campaigns.py`
    - Setup: Create test user and track
    - Test POST /campaigns (create)
    - Test GET /campaigns (list with filters)
    - Test GET /campaigns/{id} (detail)
    - Test PUT /campaigns/{id} (update)
    - Test DELETE /campaigns/{id} (delete)
    - Test POST /campaigns/{id}/duplicate
    - Test POST /campaigns/{id}/generate-content
    - Test POST /campaigns/{id}/schedule
    - Test POST /campaigns/{id}/publish
    - Test POST /campaigns/{id}/cancel
    - Test GET /campaign-templates

10.2. Test authentication
    - Test endpoints without token (401)
    - Test endpoints with invalid token (401)

10.3. Test authorization
    - Test accessing other user's campaign (403)
    - Test operations by non-creator users (403)

10.4. Test error cases
    - Invalid track_id (404)
    - Invalid campaign_id (404)
    - Invalid status for operation (400)
    - Past scheduled time (422)
    - Empty platforms array (422)

**Acceptance Criteria:**
- All endpoint tests pass
- Authentication tests pass
- Authorization tests pass
- Error handling verified
- Test coverage >80%

---

## Task 11: Documentation and Examples
**Priority:** Low  
**Estimated Time:** 2 hours  
**Dependencies:** Task 5, Task 7

Create comprehensive documentation for the Campaign Builder.

### Sub-tasks:
11.1. Create `TASK_3.2_CAMPAIGN_BUILDER_COMPLETED.md`
    - Feature overview
    - Database schema summary
    - API endpoints list
    - Usage examples
    - Integration guide
    - Testing results

11.2. Update main project documentation
    - Update README.md with campaign builder info
    - Update API documentation
    - Add campaign workflow diagrams (optional)

11.3. Create API usage examples
    - Example: Create and publish campaign
    - Example: Schedule campaign for later
    - Example: Use campaign templates
    - Example: Edit campaign content
    - Example: Search and filter campaigns

11.4. Document background scheduler setup
    - How to run scheduler
    - Platform-specific instructions
    - Troubleshooting guide

**Acceptance Criteria:**
- Completion document created
- README updated
- Usage examples provided
- Scheduler documentation complete
- All features documented

---

## Task 12: Performance Testing and Optimization
**Priority:** Low  
**Estimated Time:** 2 hours  
**Dependencies:** Task 10

Test performance and optimize if needed.

### Sub-tasks:
12.1. Test campaign list endpoint performance
    - Create 100+ test campaigns
    - Measure query time
    - Verify pagination works
    - Check index usage

12.2. Test content generation performance
    - Generate content for 4 platforms
    - Measure AI service call time
    - Test concurrent requests

12.3. Test scheduler performance
    - Create 50+ scheduled campaigns
    - Run scheduler
    - Measure activation time

12.4. Optimize if needed
    - Add database indexes if missing
    - Optimize queries
    - Add caching if beneficial

**Acceptance Criteria:**
- List endpoint <500ms for 100 campaigns
- Content generation <10s for 4 platforms
- Scheduler processes 50 campaigns <30s
- No N+1 query problems
- Proper indexes utilized

---

## Task Summary

**Total Tasks:** 12  
**Estimated Total Time:** 30.5 hours  
**Priority Breakdown:**
- High: 6 tasks (18.5 hours)
- Medium: 4 tasks (9 hours)
- Low: 2 tasks (4 hours)

**Implementation Order:**
1. Task 1: Database Models (3h)
2. Task 2: Template Seed Data (1h)
3. Task 3: Pydantic Schemas (2h)
4. Task 4: Service Layer (5h)
5. Task 5: API Endpoints (4h)
6. Task 6: Router Registration (0.5h)
7. Task 7: Background Scheduler (2h)
8. Task 8: Model Tests (2h)
9. Task 9: Service Tests (3h)
10. Task 10: Integration Tests (4h)
11. Task 11: Documentation (2h)
12. Task 12: Performance Testing (2h)

**Total Implementation Time:** 30.5 hours (~4 working days)

---

## Testing Checklist

Before marking Task 3.2 as complete, verify:

- [ ] All 4 database tables created
- [ ] 6 campaign templates seeded
- [ ] All models working correctly
- [ ] All schemas validating properly
- [ ] Campaign service methods functional
- [ ] All 15 API endpoints working
- [ ] Authentication/authorization working
- [ ] Background scheduler activating campaigns
- [ ] Unit tests passing (models + service)
- [ ] Integration tests passing (API)
- [ ] Documentation complete
- [ ] Performance acceptable
- [ ] No regressions in existing features (Task 3.1)

---

## Notes

1. **AI Service Integration:** Uses existing AIService from Task 3.1 - no changes needed to AI service itself

2. **Social Media Posting:** Content is generated and stored but not posted. Actual posting will be implemented in Task 3.3

3. **Performance Metrics:** All metrics are placeholders (default to 0) until Task 3.3 integrates real social media APIs

4. **Background Scheduler:** Recommended to run as a separate process/service for production deployment

5. **Testing:** Focus on status transitions and workflow logic as these are core to the campaign lifecycle

6. **Future Work:** Campaign analytics dashboard (charts, graphs) can be added in future phases
