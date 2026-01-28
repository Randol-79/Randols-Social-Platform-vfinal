/**
 * MongoDB Initialization Script
 * Runs on first database initialization
 */

// Switch to the randols_marketing database
db = db.getSiblingDB('randols_marketing');

// Create collections with validation schemas
print('Creating collections...');

// Content collection
db.createCollection('content', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['text', 'content_type', 'status', 'created_at'],
      properties: {
        text: { bsonType: 'string', description: 'Content text is required' },
        content_type: { 
          bsonType: 'string',
          enum: ['morning_greeting', 'daily_special', 'evening_event', 'crawfish_content', 'event_promotion', 'weekend_special', 'seasonal']
        },
        status: {
          bsonType: 'string',
          enum: ['draft', 'pending_review', 'approved', 'rejected', 'scheduled', 'published', 'failed']
        },
        platforms: { bsonType: 'array' },
        hashtags: { bsonType: 'array' },
        validation: { bsonType: 'object' },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

// Scheduled posts collection
db.createCollection('scheduled_posts', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['content_id', 'platform', 'scheduled_time', 'status'],
      properties: {
        content_id: { bsonType: 'objectId' },
        platform: { 
          bsonType: 'string',
          enum: ['instagram', 'facebook', 'tiktok', 'youtube', 'google_posts']
        },
        scheduled_time: { bsonType: 'date' },
        status: {
          bsonType: 'string',
          enum: ['pending', 'in_progress', 'completed', 'failed', 'cancelled']
        }
      }
    }
  }
});

// Create other collections
db.createCollection('daily_analytics');
db.createCollection('weekly_reports');
db.createCollection('agent_states');
db.createCollection('agent_logs');
db.createCollection('audit_logs');
db.createCollection('notifications');
db.createCollection('system_configs');
db.createCollection('ab_tests');

// Create indexes
print('Creating indexes...');

// Content indexes
db.content.createIndex({ status: 1 });
db.content.createIndex({ content_type: 1 });
db.content.createIndex({ created_at: -1 });
db.content.createIndex({ platforms: 1 });
db.content.createIndex({ 'validation.authenticity_score': 1 });
db.content.createIndex(
  { text: 'text', hashtags: 'text' },
  { weights: { text: 10, hashtags: 5 }, name: 'content_text_search' }
);

// Scheduled posts indexes
db.scheduled_posts.createIndex({ scheduled_time: 1 });
db.scheduled_posts.createIndex({ status: 1 });
db.scheduled_posts.createIndex({ platform: 1 });
db.scheduled_posts.createIndex({ content_id: 1 });
db.scheduled_posts.createIndex({ status: 1, scheduled_time: 1 });

// Analytics indexes
db.daily_analytics.createIndex({ date: -1 }, { unique: true });
db.daily_analytics.createIndex({ 'platform_breakdown.platform': 1 });

// Weekly reports
db.weekly_reports.createIndex({ week_start: -1 }, { unique: true });

// Agent indexes
db.agent_states.createIndex({ agent_name: 1 }, { unique: true });
db.agent_states.createIndex({ status: 1 });

// Agent logs with TTL (auto-delete after 30 days)
db.agent_logs.createIndex({ timestamp: -1 });
db.agent_logs.createIndex({ agent_name: 1 });
db.agent_logs.createIndex({ action_type: 1 });
db.agent_logs.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 2592000, name: 'agent_logs_ttl' }
);

// Audit logs
db.audit_logs.createIndex({ timestamp: -1 });
db.audit_logs.createIndex({ entity_type: 1 });
db.audit_logs.createIndex({ action: 1 });

// Notifications
db.notifications.createIndex({ created_at: -1 });
db.notifications.createIndex({ read: 1 });
db.notifications.createIndex({ type: 1 });

// System configs
db.system_configs.createIndex({ key: 1 }, { unique: true });

// A/B tests
db.ab_tests.createIndex({ status: 1 });
db.ab_tests.createIndex({ created_at: -1 });

// Insert default system configurations
print('Inserting default configurations...');

db.system_configs.insertMany([
  {
    key: 'posting_enabled',
    value: true,
    description: 'Enable/disable automatic posting',
    updated_at: new Date()
  },
  {
    key: 'authenticity_threshold',
    value: 0.75,
    description: 'Minimum Cajun authenticity score for content approval',
    updated_at: new Date()
  },
  {
    key: 'max_posts_per_day',
    value: 15,
    description: 'Maximum posts per day across all platforms',
    updated_at: new Date()
  },
  {
    key: 'posting_hours',
    value: { start: 6, end: 22 },
    description: 'Hours during which posts can be scheduled (CST)',
    updated_at: new Date()
  },
  {
    key: 'timezone',
    value: 'America/Chicago',
    description: 'Restaurant timezone',
    updated_at: new Date()
  },
  {
    key: 'brand_colors',
    value: {
      primary: '#C0152F',
      secondary: '#A84B2F',
      accent: '#32808D',
      gold: '#D4AF37'
    },
    description: 'Brand color palette',
    updated_at: new Date()
  },
  {
    key: 'notification_channels',
    value: ['dashboard', 'slack'],
    description: 'Enabled notification channels',
    updated_at: new Date()
  }
]);

// Initialize agent states
print('Initializing agent states...');

const agents = [
  'master_orchestrator',
  'content_generator',
  'brand_voice_guardian',
  'analytics_agent',
  'feedback_loop_agent',
  'scheduler_agent'
];

agents.forEach(agent => {
  db.agent_states.insertOne({
    agent_name: agent,
    status: 'idle',
    last_action: null,
    last_action_time: null,
    error_count: 0,
    success_count: 0,
    created_at: new Date(),
    updated_at: new Date()
  });
});

print('MongoDB initialization complete!');
print('Collections created: ' + db.getCollectionNames().join(', '));
