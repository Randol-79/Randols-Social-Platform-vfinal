# 🦞 Randol's Agentic Social Media Marketing Platform

An autonomous AI-powered social media marketing system for Randol's Restaurant in Breaux Bridge, Louisiana. Features multi-agent orchestration, authentic Cajun voice generation, and comprehensive analytics.

![Randol's Marketing Platform](https://via.placeholder.com/800x400/C0152F/FFFFFF?text=Randol%27s+Marketing+Platform)

---

## 🚀 One-Click Deploy

Deploy to your preferred platform with one click:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/randols/marketing-platform)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/randols/marketing-platform&env=NEXT_PUBLIC_API_URL&envDescription=Backend%20API%20URL)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/randols-platform)

---

## ⚡ Quick Start (60 seconds)

### Option 1: One-Click Setup Script

**macOS/Linux:**
```bash
git clone https://github.com/randols/marketing-platform.git
cd marketing-platform
chmod +x setup.sh && ./setup.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/randols/marketing-platform.git
cd marketing-platform
.\setup.ps1
```

### Option 2: Make Command (Cross-platform)
```bash
# Installs dependencies and starts frontend + backend
make install && make dev
```

### Option 3: Docker (Recommended for production-like environment)
```bash
cp .env.example .env
# Edit .env with your API keys
docker-compose up
```

### Development quickstart (dev-optimized, fast feedback)
```bash
# Frontend only (hot reload):
cd frontend && npm install && npm run dev

# Backend only (watching not configured by default):
cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt && python main.py

# Start both locally using make (cross-platform):
make dev

# Run tests:
make test
```

**Local development checklist (recommended)**
- Install Docker Desktop (recommended) so you can run MongoDB and Redis locally.
- Create `.env` (automatically generated with secure defaults via `scripts/generate_env.py` or run `.\setup.ps1` on Windows). For non-interactive runs you can set `NONINTERACTIVE=1`.
- Start just the DB services locally: `make docker-db-up`.
- Initialize the database (samples): `make db-init` or `python backend/scripts/init_db.py --samples`.
- Start the apps:
  - Backend: `make dev-backend` (or `cd backend && .\venv\Scripts\Activate.ps1 && python main.py` on Windows)
  - Frontend: `make dev-frontend`

**That's it!** Open http://localhost:3000

---

## 📱 Mobile-Ready PWA

The dashboard is a Progressive Web App optimized for mobile:

- **Install on iPhone/Android**: Open in browser → "Add to Home Screen"
- **Touch-optimized**: 44px+ tap targets, swipe gestures
- **Offline support**: Core features work offline
- **Push notifications**: Get alerts for content performance

---

## ✨ Features

### 🤖 Multi-Agent AI System
| Agent | Purpose |
|-------|---------|
| **Master Orchestrator** | Central coordination hub |
| **Content Generator** | GPT-4 powered content with token tracking |
| **Brand Voice Guardian** | V.A.U.L.T. framework validation |
| **Analytics Agent** | Performance tracking & insights |
| **Feedback Loop Agent** | A/B testing & optimization |
| **Scheduler Agent** | Intelligent posting queue |
| **Platform Agents** | Instagram, Facebook, TikTok, YouTube, Google Posts |

### 🎵 Authentic Cajun Voice
- Louisiana cultural references
- Cajun phrases and expressions
- Authenticity scoring (0.75+ threshold)
- Stereotype avoidance
- Seasonal terminology (crawfish season, Mardi Gras)

### 📊 Comprehensive Analytics
- Real-time engagement tracking
- Platform performance comparison
- Content type analysis
- AI-powered recommendations
- Weekly automated reports

### 🔒 Enterprise Security
- API key authentication with rate limiting
- Token usage tracking and cost estimation
- OpenTelemetry observability
- Automatic retry with exponential backoff
- Environment variable validation

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js PWA)                     │
│    Dashboard │ Content │ Calendar │ Analytics │ Agents │ Brand   │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                          REST API / WebSocket
                               │
┌──────────────────────────────┴───────────────────────────────────┐
│                      BACKEND (Flask + Python)                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Master Orchestrator                       │ │
│  │                    (Agent Registry)                          │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
│            ┌────────────────┼────────────────┐                   │
│            ▼                ▼                ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │
│  │   Content    │ │  Brand Voice │ │  Analytics   │              │
│  │  Generator   │ │   Guardian   │ │    Agent     │              │
│  │   (GPT-4)    │ │  (V.A.U.L.T) │ │              │              │
│  └──────────────┘ └──────────────┘ └──────────────┘              │
│          │                                                       │
│          ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              LLM Client (Token Tracking)                  │   │
│  │   • Cost estimation • Retry logic • OpenTelemetry        │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ MongoDB  │    │  Redis   │    │  OpenAI  │
        │  Atlas   │    │  Cache   │    │   API    │
        └──────────┘    └──────────┘    └──────────┘
```

---

## 📁 Project Structure

```
randols-platform/
├── backend/                  # Python Flask API
│   ├── agents/               # AI Agent implementations
│   │   └── registry.py       # Singleton agent management
│   ├── api/                  # REST API routes
│   ├── database/             # MongoDB models & repos
│   ├── middleware/           # Auth, rate limiting
│   ├── utils/
│   │   ├── llm_client.py     # LLM with token tracking
│   │   ├── prompt_patterns.py # GENERATOR/VALIDATOR prompts
│   │   └── telemetry.py      # OpenTelemetry
│   └── main.py               # Entry point
│
├── frontend/                 # Next.js PWA
│   ├── app/                  # Pages (App Router)
│   ├── components/           # React components
│   ├── styles/               # Mobile-optimized CSS
│   └── public/manifest.json  # PWA config
│
├── .github/workflows/ci.yml  # CI/CD pipeline
├── docker-compose.yml        # Container orchestration
├── render.yaml               # Render deployment
├── vercel.json               # Vercel deployment
├── railway.toml              # Railway deployment
├── setup.sh                  # Unix setup script
├── setup.ps1                 # Windows setup script
├── .env.example              # Environment template
├── .env.schema.json          # Validation schema
└── Makefile                  # Development commands
```

---

## 🔧 Configuration

### Required Environment Variables

```bash
# AI (Required)
OPENAI_API_KEY=sk-your-key-here

# Database (Required)
MONGODB_URI=mongodb+srv://...

# Security (Auto-generated by setup script)
SECRET_KEY=auto-generated
JWT_SECRET_KEY=auto-generated
```

### Optional Platform Credentials

| Platform | Variables |
|----------|-----------|
| Instagram | `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID` |
| Facebook | `FACEBOOK_ACCESS_TOKEN`, `FACEBOOK_PAGE_ID` |

---

## 🔐 GitHub Actions Secrets & Validation Helper ✅

I've added a workflow that helps you validate required CI/CD secrets and repository Actions permissions, and can optionally trigger a test Render deployment.

1) Add repository secrets (Settings → Secrets → Actions):
   - `RENDER_API_KEY` (if using Render)
   - `RENDER_SERVICE_ID` (if using Render)
   - `VERCEL_TOKEN` (if using Vercel)
   - `VERCEL_PROJECT_ID` (if using Vercel)
   - `DOCKERHUB_USERNAME` (optional fallback)
   - `DOCKERHUB_TOKEN` (optional fallback)

2) Run the validation workflow in GitHub UI: `.github/workflows/validate-secrets.yml` → `Run workflow`.
   - Optional input: `trigger_render_deploy=true` to automatically trigger a Render deploy if both `RENDER_*` secrets are present.

3) From the command line (with GitHub CLI installed):

```bash
# Validate secrets (no deploy)
gh workflow run validate-secrets.yml --repo <owner>/<repo>

# Validate and trigger a Render deploy (only if RENDER secrets are set)
gh workflow run validate-secrets.yml --repo <owner>/<repo> -f trigger_render_deploy=true
```

4) What the workflow checks:
   - Presence of required secrets listed above
   - Repository Actions permissions (it reads the 'actions' permissions and reports them)
   - If `trigger_render_deploy` is true and Render secrets exist, it triggers a Render deploy via the Render API and reports the result.

> Important: Do not paste secrets into PR comments or chat. Use the repository Secrets UI or `gh secret set` / GitHub UI to add them securely.

---

If you'd like, I can also:
- Add an automated check that fails CI if critical secrets are missing (recommended for locked-down repos).
- Add a `gh` helper script to set secrets from your machine using `gh secret set` (safe and local).

| TikTok | `TIKTOK_ACCESS_TOKEN`, `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` |
| YouTube | `YOUTUBE_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |

See [.env.example](.env.example) for complete configuration.

---

## 🛠️ Development Commands

```bash
# Setup
make install          # Install all dependencies
make dev              # Start development servers

# Testing
make test             # Run all tests
make coverage         # Run with coverage report

# Code Quality
make lint             # Run linters
make format           # Format code

# Docker
make docker-up        # Start Docker services
make docker-down      # Stop services
make docker-logs      # View logs

# Utilities
make health           # Check service health
make llm-stats        # View LLM usage statistics
make validate-env     # Validate environment config
```

---

## 📚 API Endpoints

### Base URL: `http://localhost:5000/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| GET | `/status` | Comprehensive status |
| **Content** | | |
| GET | `/content` | List all content |
| POST | `/content` | Create content |
| POST | `/content/generate` | AI generate content |
| POST | `/content/validate` | Validate brand voice |
| **Scheduling** | | |
| GET | `/schedule` | Get scheduled posts |
| POST | `/schedule` | Schedule content |
| GET | `/schedule/calendar` | Calendar view |
| **Analytics** | | |
| GET | `/analytics/daily` | Daily analytics |
| GET | `/analytics/performance` | Performance analysis |
| GET | `/analytics/recommendations` | AI recommendations |
| **Agents** | | |
| GET | `/agents` | List agent status |
| POST | `/admin/pause` | Pause all agents |
| POST | `/admin/resume` | Resume all agents |

---

## 📱 Mobile Features

### Touch Optimizations
- Minimum 44px touch targets
- Safe area insets for notched devices
- Swipe-to-navigate gestures
- Pull-to-refresh on data views

### Responsive Breakpoints
```css
xs: 375px   /* Small phones */
sm: 640px   /* Large phones */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
```

### Accessibility
- Reduced motion support
- High contrast mode
- Screen reader optimized
- Keyboard navigation

---

## 🧪 Testing

```bash
# Backend tests with coverage
cd backend && pytest tests/ -v --cov=. --cov-report=html

# Frontend tests
cd frontend && npm test -- --coverage

# E2E tests (if configured)
npm run test:e2e
```

---

## 📊 V.A.U.L.T. Framework

The Brand Voice Guardian uses the V.A.U.L.T. framework:

| Letter | Meaning | Implementation |
|--------|---------|----------------|
| **V** | Voice Foundation | Authentic Cajun hospitality |
| **A** | Audience Adaptations | Platform/demographic targeting |
| **U** | Unique Flavor | Signature phrases and cultural references |
| **L** | Language Patterns | Natural Cajun expressions |
| **T** | Tone Requirements | Warm, conversational, storytelling |

### Authenticity Scoring
| Score | Status | Action |
|-------|--------|--------|
| 0.75+ | ✅ Approved | Auto-publish |
| 0.50-0.74 | ⚠️ Review | Manual review |
| < 0.50 | ❌ Rejected | Regenerate |

---

## 🚢 Deployment

### Render.com (Recommended)

1. Click "Deploy to Render" button above
2. Connect your GitHub account
3. Configure environment variables
4. Deploy automatically

### Vercel + Render Split

```bash
# Frontend → Vercel
vercel deploy --prod

# Backend → Render
# Auto-deploys from render.yaml
```

### Railway

```bash
railway login
railway init
railway up
```

### Manual Deployment

```bash
# Backend (Gunicorn)
cd backend
gunicorn --worker-class eventlet -w 4 main:app

# Frontend (Next.js)
cd frontend
npm run build && npm start
```

---

## 📈 Observability

### LLM Usage Tracking
```python
from utils.llm_client import get_llm_client
stats = get_llm_client().get_stats()
# Returns: tokens used, cost, latency, error rate
```

### OpenTelemetry
Set `OTEL_EXPORTER_OTLP_ENDPOINT` for distributed tracing.

### Metrics Available
- `content_generated_total` - Content items created
- `llm_requests_total` - LLM API calls
- `llm_tokens_total` - Tokens consumed
- `llm_cost_total` - Cost in cents
- `posts_published_total` - Posts published

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

Proprietary - Randol's Restaurant © 2024

---

<div align="center">

**Randol's Restaurant**
*Breaux Bridge, Louisiana - Est. 1973*

🦞 *Authentic Cajun Cuisine & Live Zydeco Music* 🎵

**Laissez les bon temps rouler!**

</div>
