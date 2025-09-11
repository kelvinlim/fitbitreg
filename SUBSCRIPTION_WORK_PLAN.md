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

#### 1.2 Create Fitbit Data Storage Table
```sql
CREATE TABLE fitbitdata (
    id INTEGER PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    subscription_id INTEGER REFERENCES fitbit_subscriptions(id),
    collection_type VARCHAR(100) NOT NULL,  -- 'activities', 'sleep', 'heart', etc.
    data_date DATE NOT NULL,               -- Date of the data
    data_type VARCHAR(100),                -- Specific data type (e.g., 'steps', 'heart_rate_zones')
    raw_data JSON,                         -- Complete raw data from Fitbit API
    processed_data JSON,                   -- Processed/cleaned data
    data_source VARCHAR(50) DEFAULT 'subscription', -- 'subscription', 'manual', 'polling'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, collection_type, data_date, data_type)
);
```

#### 1.3 Add Subscription Fields to Accounts Table
```sql
ALTER TABLE accounts ADD COLUMN subscription_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE accounts ADD COLUMN webhook_secret VARCHAR(255);
```

#### 1.4 Create Notification Log Table
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
- `store_fitbit_data(account_id, collection_type, data_date, data_type, raw_data, processed_data)`
- `get_fitbit_data(account_id, collection_type, start_date, end_date)`
- `update_fitbit_data(data_id, raw_data, processed_data)`

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

#### 2.3 Data Processing Module
- Create `fitbit_data_processor.py` module
- Implement data fetching from Fitbit API based on notifications
- Data parsing and normalization for different collection types
- Data validation and error handling
- Support for incremental data updates

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
    # Fetch and store new data
    # Update user data
```

#### 3.3 Data Processing Routes
```python
@app.route(f"{APP_PATH}/data/<collection_type>", methods=['GET'])
@app.route(f"{APP_PATH}/data/<collection_type>/<date>", methods=['GET'])
@app.route(f"{APP_PATH}/data/refresh/<collection_type>", methods=['POST'])
```

#### 3.4 User Interface Routes
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

### Data Processing Workflow
1. **Notification Received**: Fitbit sends webhook notification
2. **Verification**: Verify HMAC signature for security
3. **Data Fetching**: Use stored OAuth token to fetch data from Fitbit API
4. **Data Processing**: Parse and normalize data based on collection type
5. **Data Storage**: Store both raw and processed data in `fitbitdata` table
6. **Notification Logging**: Log the notification for audit purposes

### Fitbit API Endpoints to Implement
1. **Create Subscription**: `POST /1/user/-/{collection-path}/apiSubscriptions/{subscription-id}.json`
2. **Delete Subscription**: `DELETE /1/user/-/{collection-path}/apiSubscriptions/{subscription-id}.json`
3. **List Subscriptions**: `GET /1/user/-/{collection-path}/apiSubscriptions.json`
4. **Fetch Data**: `GET /1/user/{user-id}/{collection-path}/date/{date}.json`

### Collection Paths to Support
- `activities` - Activity data (steps, calories, distance, active minutes)
- `sleep` - Sleep data (sleep stages, duration, efficiency)
- `heart` - Heart rate data (resting HR, HR zones, HR variability)
- `body` - Body measurements (weight, BMI, body fat)
- `nutrition` - Nutrition data (calories, water, food logs)
- `weight` - Weight data (daily weight measurements)

### Data Processing by Collection Type

#### Activities Data
- **Raw Data**: Complete activity summary from Fitbit API
- **Processed Data**: Extracted metrics (steps, calories, active minutes, distance)
- **Data Types**: `daily_summary`, `intraday_steps`, `intraday_calories`

#### Sleep Data
- **Raw Data**: Complete sleep log with stages and details
- **Processed Data**: Sleep efficiency, duration, stage breakdown
- **Data Types**: `sleep_log`, `sleep_stages`, `sleep_efficiency`

#### Heart Rate Data
- **Raw Data**: Heart rate zones, resting HR, HR variability
- **Processed Data**: Normalized HR metrics and trends
- **Data Types**: `heart_rate_zones`, `resting_heart_rate`, `hrv_data`

#### Body/Nutrition/Weight Data
- **Raw Data**: Complete measurement data
- **Processed Data**: Normalized measurements and trends
- **Data Types**: `weight_log`, `body_fat`, `bmi`, `nutrition_log`

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
- [ ] Data is automatically fetched and stored when notifications arrive
- [ ] Both raw and processed data are stored in `fitbitdata` table
- [ ] Data can be queried by collection type, date range, and data type
- [ ] Admin can monitor subscription status and data storage
- [ ] Error handling and logging are comprehensive
- [ ] Performance is maintained under load
- [ ] Data integrity is maintained with proper validation

## Risk Mitigation
- Implement graceful degradation if subscriptions fail
- Maintain polling as fallback option
- Comprehensive error logging and monitoring
- Regular testing of webhook endpoints
- Backup and recovery procedures

## Timeline Estimate
**Total Estimated Time: 25-30 hours**
- Phase 1-3: 12-15 hours (Core functionality + Data processing)
- Phase 4-5: 5-7 hours (UI and Security)
- Phase 6-7: 5-6 hours (Testing and Deployment)
- Additional 3-5 hours for data processing and storage implementation

## Next Steps
1. Review and approve this work plan
2. Set up development environment
3. Begin with Phase 1 (Database Schema)
4. Implement incrementally with testing at each phase
5. Deploy to staging environment for testing
6. Production deployment with monitoring

