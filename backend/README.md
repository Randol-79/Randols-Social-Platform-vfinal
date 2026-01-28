# Randol's Agentic Marketing Platform - Backend

## 🦞 Overview

The backend for Randol's Restaurant's autonomous social media marketing platform. This system uses multi-agent AI architecture to generate, validate, schedule, and optimize content across multiple social media platforms while maintaining authentic Cajun voice and cultural appropriateness.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Master Orchestrator                          │
│         (Central Coordination & Workflow Management)            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Content     │   │  Brand Voice  │   │   Analytics   │
│  Generator    │   │   Guardian    │   │    Agent      │
│   (GPT-4)     │   │  (V.A.U.L.T.) │   │ (Performance) │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────────────────────────────────────────────────────┐
│                      Scheduler Agent                           │
│           (Queue Management & Optimal Timing)                  │
└───────────────────────────┬───────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Instagram    │   │   Facebook    │   │    TikTok     │
│    Agent      │   │    Agent      │   │    Agent      │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   YouTube     │   │ Google Posts  │
│    Agent      │   │    Agent      │
└───────────────┘   └───────────────┘
        │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                ┌───────────────────┐
                │  Feedback Loop    │
                │     Agent         │
                │ (A/B Testing &    │
                │  Optimization)    │
                └───────────────────┘
```

## 📁 Directory Structure

```
backend/
├── agents/                     # AI Agent implementations
│   ├── master_orchestrator.py  # Central coordination
│   ├── content_generator.py    # AI content creation
│   ├── brand_voice_guardian.py # V.A.U.L.T. validation
│   ├── analytics_agent.py      # Performance analytics
│   ├── feedback_loop_agent.py  # A/B testing & optimization
│   ├── scheduler_agent.py      # Content scheduling
│   └── platform_agents.py      # Platform-specific agents
│
├── api/                        # Flask API
│   ├── app.py                  # Main Flask application
│   └── routes.py               # API route definitions
│
├── database/                   # Database layer
│   ├── models.py               # Pydantic models
│   └── repository.py           # MongoDB repositories
│
├── jobs/                       # Scheduled jobs
│   ├── daily_content_generation.py
│   ├── analytics_sync.py
│   └── weekly_report.py
│
├── workers/                    # Background workers
│   └── scheduler_worker.py     # Continuous schedule processor
│
├── utils/                      # Utilities
│   ├── config.py               # Configuration management
│   ├── cajun_voice.py          # Cajun voice processor
│   ├── prompt_templates.py     # AI prompt templates
│   └── logger.py               # Logging setup
│
├── scripts/                    # Utility scripts
│   ├── init_db.py              # Database initialization
│   └── start.sh                # Startup script
│
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest configuration
│   └── test_platform.py        # Platform tests
│
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── Dockerfile                  # Docker configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB Atlas or local MongoDB
- Redis (optional but recommended)
- OpenAI API key

### Installation

```bash
# Clone repository
git clone <repo-url>
cd randols-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your credentials

# Initialize database
python scripts/init_db.py --samples

# Start development server
python main.py
```

### Using the Startup Script

```bash
# Make executable
chmod +x scripts/start.sh

# Start development server
./scripts/start.sh dev

# Start production server
./scripts/start.sh prod

# Start background worker
./scripts/start.sh worker

# Initialize database
./scripts/start.sh init

# Run tests
./scripts/start.sh test
```

## 🔧 Configuration

### Environment Variables

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key

# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/randols_marketing

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# OpenAI
OPENAI_API_KEY=sk-...

# Social Media APIs
INSTAGRAM_ACCESS_TOKEN=...
FACEBOOK_ACCESS_TOKEN=...
TIKTOK_ACCESS_TOKEN=...
YOUTUBE_API_KEY=...
GOOGLE_POSTS_API_KEY=...

# Webhooks
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# Feature Flags
AI_GENERATION_ENABLED=true
AUTO_SCHEDULING_ENABLED=true
```

## 📚 API Reference

### Base URL
```
http://localhost:5000/api/v1
```

### Authentication
Currently uses API key authentication (add `X-API-Key` header)

### Endpoints

#### Health & Status
```
GET  /health              # System health check
GET  /status              # Comprehensive status
GET  /config              # Public configuration
```

#### Content Management
```
GET  /content             # List content
POST /content             # Create content
GET  /content/{id}        # Get content by ID
PUT  /content/{id}        # Update content
DELETE /content/{id}      # Archive content
POST /content/generate    # AI-generate content
POST /content/validate    # Validate content
POST /content/enhance     # Enhance with Cajun voice
```

#### Scheduling
```
GET  /schedule            # Get scheduled posts
POST /schedule            # Schedule content
GET  /schedule/pending    # Get pending posts
GET  /schedule/calendar   # Get calendar view
POST /schedule/{id}/cancel # Cancel scheduled post
GET  /schedule/optimal-times # Get optimal posting times
```

#### Analytics
```
GET  /analytics/daily     # Daily analytics
GET  /analytics/range     # Date range analytics
GET  /analytics/weekly    # Weekly reports
GET  /analytics/platform/{platform}  # Platform analytics
GET  /analytics/performance  # Performance analysis
GET  /analytics/recommendations  # AI recommendations
```

#### Agents
```
GET  /agents              # List all agents
GET  /agents/{name}       # Get agent status
GET  /agents/{name}/logs  # Get agent logs
GET  /agents/logs/errors  # Get error logs
```

#### Admin
```
POST /admin/emergency-override  # Trigger emergency
POST /admin/pause              # Pause system
POST /admin/resume             # Resume system
POST /admin/run-workflow       # Run daily workflow
POST /admin/ab-test            # Start A/B test
GET  /admin/notifications      # Get notifications
```

#### Brand
```
GET  /brand/guidelines    # Brand voice guidelines
GET  /brand/cajun-phrases # Cajun phrases & references
```

## 🤖 Agents

### Master Orchestrator
Central coordination hub managing all agent interactions and workflow execution.

**Responsibilities:**
- Daily workflow execution
- Agent coordination
- Emergency override handling
- System status monitoring

### Content Generator
AI-powered content creation using GPT-4 with Cajun voice enhancement.

**Features:**
- Context-aware generation
- Platform-optimized content
- Seasonal content adaptation
- Emergency content generation

### Brand Voice Guardian
Validates content authenticity using the V.A.U.L.T. framework.

**V.A.U.L.T. Framework:**
- **V**oice Foundation - Authentic Cajun hospitality
- **A**udience Adaptations - Platform/demographic targeting
- **U**nique Flavor - Signature phrases and references
- **L**anguage Patterns - Natural Cajun expressions
- **T**one Requirements - Warm, conversational, storytelling

### Analytics Agent
Tracks and analyzes performance across all platforms.

**Metrics:**
- Engagement rates
- Reach and impressions
- Content type performance
- Posting time optimization

### Feedback Loop Agent
Continuous optimization through A/B testing and machine learning.

**Features:**
- A/B test management
- Performance trending
- Automatic optimization triggers
- Strategy recommendations

### Scheduler Agent
Manages content queue and optimal posting times.

**Features:**
- Priority-based queue
- Platform rate limiting
- Conflict resolution
- Optimal time calculation

### Platform Agents
Platform-specific posting and optimization.

**Supported Platforms:**
- Instagram (Graph API)
- Facebook (Graph API)
- TikTok (TikTok API)
- YouTube (Data API v3)
- Google Business Profile

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=.

# Run specific test file
pytest tests/test_platform.py -v

# Run specific test
pytest tests/test_platform.py::TestBrandVoiceGuardian -v
```

## 📊 Database Schema

### Collections

- **content** - Content documents with validation and metrics
- **scheduled_posts** - Scheduled posting queue
- **daily_analytics** - Daily performance summaries
- **weekly_reports** - Weekly performance reports
- **agent_states** - Agent status and health
- **agent_logs** - Agent activity logs (30-day TTL)
- **audit_logs** - System change audit trail
- **notifications** - System notifications
- **system_configs** - Runtime configuration
- **ab_tests** - A/B test configurations and results

## 🔄 Background Jobs

### Daily Content Generation (6 AM)
Generates full day's content based on context (weather, events, season).

### Analytics Sync (Every 4 hours)
Collects performance metrics from all platforms.

### Weekly Report (Monday 8 AM)
Comprehensive weekly performance report with recommendations.

## 🚢 Deployment

### Render.com

```bash
# Deploy using render.yaml blueprint
# Push to GitHub, Render auto-deploys
```

### Docker

```bash
# Build image
docker build -t randols-backend ./backend

# Run container
docker run -p 5000:5000 --env-file .env randols-backend
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## 📈 Monitoring

### Health Checks
- `/api/v1/health` - Basic health check
- `/api/v1/status` - Detailed system status
- `/api/v1/admin/database/health` - Database health

### Logging
Structured logging with configurable levels:
- DEBUG - Development debugging
- INFO - General information
- WARNING - Potential issues
- ERROR - Error conditions

### Alerts
- Slack webhook notifications
- Discord webhook notifications
- Email alerts (configurable)

## 🔒 Security

- API key authentication
- CORS configuration
- Rate limiting
- Input validation
- SQL injection prevention (MongoDB)
- XSS protection headers

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

Proprietary - Randol's Restaurant

---

**Laissez les bon temps rouler!** 🦞🎵
