# Fitbit Subscription Integration Work Plan

## Overview
This document outlines the comprehensive plan to add Fitbit subscription capabilities to the `kolim/fitbitreg` Flask application, enabling real-time data notifications instead of polling.

## Current System Analysis

### Existing OAuth Flow
- ✅ OAuth 2.0 with PKCE implementation
- ✅ Token storage in `Accounts` table
- ✅ User registration via entry codes
- ✅ Token refresh capability

### Current Database Schema
- `Accounts` table stores OAuth tokens, user IDs, and Fitbit data
- `Garmindata` table for wearable data storage
- `Study` table for study management

## Work Plan

### Phase 1: Database Schema Enhancement
**Priority: High | Estimated Time: 2-3 hours**

#### 1.1 Create Subscription Table
```sql
CREATE TABLE fitbit_subscriptions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    subscription_id VARCHAR(255) UNIQUE NOT NULL,
    collection_path VARCHAR(100) NOT NULL,  -- e.g., 'activities', 'sleep', 'heart'
    subscription_type VARCHAR(50) NOT NULL, -- 'user' or 'all'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_notification DATETIME,
    notification_count INTEGER DEFAULT 0
);
```

#### 1.2 Add Subscription Fields to Accounts Table
```sql
ALTER TABLE accounts ADD COLUMN subscription_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE accounts ADD COLUMN webhook_secret VARCHAR(255);
```

#### 1.3 Create Notification Log Table
```sql
CREATE TABLE subscription_notifications (
    id INTEGER PRIMARY KEY,
    subscription_id INTEGER REFERENCES fitbit_subscriptions(id),
    notification_data JSON,
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    error_message TEXT
);
```

### Phase 2: Core Subscription Management
**Priority: High | Estimated Time: 4-5 hours**

#### 2.1 Database Methods (db_code.py)
- `create_subscription(account_id, collection_path, subscription_type)`
- `delete_subscription(subscription_id)`
- `get_user_subscriptions(account_id)`
- `update_subscription_status(subscription_id, is_active)`
- `log_notification(subscription_id, notification_data)`

#### 2.2 Fitbit API Integration
- Create `fitbit_subscription_manager.py` module
- Implement subscription CRUD operations
- Handle API authentication and error handling
- Support for all Fitbit collection paths:
  - `activities`
  - `sleep`
  - `heart`
  - `body`
  - `nutrition`
  - `weight`

### Phase 3: Flask Routes Implementation
**Priority: High | Estimated Time: 3-4 hours**

#### 3.1 Subscription Management Routes
```python
# New routes to add to fitbit_flask.py
@app.route(f"{APP_PATH}/subscriptions", methods=['GET', 'POST'])
@app.route(f"{APP_PATH}/subscriptions/<int:subscription_id>", methods=['DELETE'])
@app.route(f"{APP_PATH}/subscriptions/status", methods=['GET'])
```

#### 3.2 Webhook Handler
```python
@app.route(f"{APP_PATH}/webhook/fitbit", methods=['POST'])
def fitbit_webhook():
    # Handle incoming Fitbit notifications
    # Verify signature
    # Process notification
    # Update user data
```

#### 3.3 User Interface Routes
```python
@app.route(f"{APP_PATH}/manage-subscriptions")
@app.route(f"{APP_PATH}/subscription-history")
```

### Phase 4: User Interface Enhancement
**Priority: Medium | Estimated Time: 3-4 hours**

#### 4.1 Subscription Management UI
- Add subscription management to existing user dashboard
- Create subscription status page
- Add enable/disable subscription controls
- Display subscription history and notifications

#### 4.2 Admin Interface
- Subscription monitoring dashboard
- User subscription status overview
- Notification log viewer
- Error handling and debugging tools

### Phase 5: Security and Validation
**Priority: High | Estimated Time: 2-3 hours**

#### 5.1 Webhook Security
- Implement HMAC signature verification
- Add rate limiting for webhook endpoints
- Validate notification payloads
- Handle malformed requests gracefully

#### 5.2 Error Handling
- Comprehensive error logging
- Retry mechanisms for failed API calls
- User-friendly error messages
- Monitoring and alerting

### Phase 6: Testing and Validation
**Priority: High | Estimated Time: 3-4 hours**

#### 6.1 Unit Tests
- Test subscription CRUD operations
- Test webhook handling
- Test error scenarios
- Test token refresh integration

#### 6.2 Integration Testing
- End-to-end subscription flow
- Webhook simulation testing
- Performance testing
- Load testing

### Phase 7: Deployment and Monitoring
**Priority: Medium | Estimated Time: 2-3 hours**

#### 7.1 Configuration Updates
- Update environment variables
- Configure webhook URLs in Fitbit developer portal
- Update nginx configuration if needed
- Docker configuration updates

#### 7.2 Monitoring Setup
- Add subscription status monitoring
- Set up notification failure alerts
- Performance metrics collection
- Log aggregation

## Implementation Details

### Fitbit API Endpoints to Implement
1. **Create Subscription**: `POST /1/user/-/{collection-path}/apiSubscriptions/{subscription-id}.json`
2. **Delete Subscription**: `DELETE /1/user/-/{collection-path}/apiSubscriptions/{subscription-id}.json`
3. **List Subscriptions**: `GET /1/user/-/{collection-path}/apiSubscriptions.json`

### Collection Paths to Support
- `activities` - Activity data
- `sleep` - Sleep data
- `heart` - Heart rate data
- `body` - Body measurements
- `nutrition` - Nutrition data
- `weight` - Weight data

### Webhook Payload Structure
```json
{
  "collectionType": "activities",
  "date": "2024-01-01",
  "ownerId": "user_id",
  "ownerType": "user",
  "subscriptionId": "subscription_id"
}
```

## Dependencies to Add
- `cryptography` - For HMAC signature verification
- `flask-limiter` - For rate limiting
- `celery` - For background task processing (optional)

## Configuration Updates
Add to `.env`:
```
FITBIT_WEBHOOK_SECRET=your_webhook_secret
FITBIT_API_BASE_URL=https://api.fitbit.com
SUBSCRIPTION_ENABLED=true
```

## Success Criteria
- [ ] Users can enable/disable subscriptions for different data types
- [ ] Real-time notifications are received and processed
- [ ] Data is automatically updated when notifications arrive
- [ ] Admin can monitor subscription status
- [ ] Error handling and logging are comprehensive
- [ ] Performance is maintained under load

## Risk Mitigation
- Implement graceful degradation if subscriptions fail
- Maintain polling as fallback option
- Comprehensive error logging and monitoring
- Regular testing of webhook endpoints
- Backup and recovery procedures

## Timeline Estimate
**Total Estimated Time: 20-25 hours**
- Phase 1-3: 9-12 hours (Core functionality)
- Phase 4-5: 5-7 hours (UI and Security)
- Phase 6-7: 5-6 hours (Testing and Deployment)

## Next Steps
1. Review and approve this work plan
2. Set up development environment
3. Begin with Phase 1 (Database Schema)
4. Implement incrementally with testing at each phase
5. Deploy to staging environment for testing
6. Production deployment with monitoring

