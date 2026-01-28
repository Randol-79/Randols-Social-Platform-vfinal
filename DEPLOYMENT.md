# 🚀 Randol's Platform - Deployment Guide

## Pre-Deployment Checklist

### ✅ Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `MONGODB_URI` (MongoDB Atlas recommended)
- [ ] Set `OPENAI_API_KEY` 
- [ ] Set `API_KEY` (generate with `python -c "import secrets; print(f'rnd_{secrets.token_urlsafe(32)}')"`)
- [ ] Set `SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Set `JWT_SECRET` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Configure social media API tokens (Instagram, Facebook, TikTok, YouTube)

### ✅ Database Setup
- [ ] MongoDB Atlas cluster created
- [ ] Database user with read/write access
- [ ] IP whitelist configured (or 0.0.0.0/0 for Render)
- [ ] Connection string tested

### ✅ Social Media APIs
- [ ] Meta Developer account created
- [ ] Instagram Graph API access token
- [ ] Facebook Page access token
- [ ] TikTok API credentials (optional)
- [ ] YouTube Data API key (optional)

### ✅ Notification Setup (Optional)
- [ ] Slack webhook URL configured
- [ ] Discord webhook URL configured
- [ ] Email SMTP settings configured

---

## Quick Start Commands

### Local Development

```bash
# 1. Clone and setup
git clone <repository-url>
cd randols-platform

# 2. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 3. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Validate environment
python utils/env_validation.py --show-config

# 5. Initialize database
python scripts/init_db.py --samples

# 6. Start backend
python main.py
# API available at http://localhost:5000

# 7. Frontend setup (new terminal)
cd frontend
npm install

# 8. Start frontend
npm run dev
# Dashboard available at http://localhost:3000
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Production Deployment

#### Render.com (Recommended)

1. Connect GitHub repository to Render
2. Render auto-detects `render.yaml`
3. Configure environment variables in Render dashboard
4. Deploy

#### Manual Docker

```bash
# Build images
docker build -t randols-backend ./backend
docker build -t randols-frontend ./frontend

# Run with environment file
docker run -d --env-file .env -p 5000:5000 randols-backend
docker run -d -p 3000:3000 randols-frontend
```

---

## API Testing

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Get status (with API key)
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/v1/status

# Generate content
curl -X POST http://localhost:5000/api/v1/content/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"content_type": "daily_special", "platforms": ["instagram", "facebook"]}'

# Validate content
curl -X POST http://localhost:5000/api/v1/content/validate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "Fresh crawfish today, cher! Come get them while they are hot!"}'
```

---

## Troubleshooting

### Common Issues

**MongoDB Connection Failed**
```
Check: MONGODB_URI format
Check: IP whitelist in Atlas
Check: Network connectivity
```

**OpenAI API Error**
```
Check: OPENAI_API_KEY is valid
Check: API quota not exceeded
Check: Model name is correct
```

**Rate Limiting**
```
Check: RATE_LIMIT_ENABLED setting
Check: Redis connection (if using)
Adjust: RATE_LIMIT_PER_MINUTE
```

**CORS Errors**
```
Check: CORS_ORIGINS includes frontend URL
Check: API_URL in frontend .env
```

### Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend

# Render logs
render logs --service randols-backend
```

---

## Security Notes

1. **Never commit `.env` files** - Contains secrets
2. **Rotate API keys regularly** - Every 90 days recommended
3. **Use strong secrets** - At least 32 characters
4. **Enable rate limiting** - Protect against abuse
5. **Monitor error logs** - Watch for suspicious activity

---

## Support

- Documentation: `/api/v1/docs`
- Health Check: `/api/v1/health`
- Status: `/api/v1/status`

**Laissez les bon temps rouler!** 🦞🎵
