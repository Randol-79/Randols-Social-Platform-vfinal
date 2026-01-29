#!/usr/bin/env python3
"""
Database Initialization and Setup Script
Randol's Agentic Marketing Platform

This script initializes the MongoDB database with:
- Required indexes
- Default configurations
- Sample data (optional)
- System settings
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger("db_init")


async def check_connection():
    """Check MongoDB connection"""
    from database import db_manager

    logger.info("Checking database connection...")
    health = await db_manager.check_health_async()

    if health["status"] != "healthy":
        logger.error(f"Database connection failed: {health.get('error')}")
        return False

    logger.info(f"Database connected: {health['database']}")
    return True


async def create_indexes():
    """Create database indexes"""
    from database import db_manager

    logger.info("Creating database indexes...")
    await db_manager.create_indexes()
    logger.info("Indexes created successfully")


async def create_default_configs():
    """Create default system configurations"""
    from database import db_manager

    db = db_manager.get_async_db()
    configs_collection = db["system_configs"]

    default_configs = [
        {
            "key": "posting_enabled",
            "value": True,
            "description": "Master switch for automated posting",
            "category": "system",
        },
        {
            "key": "content_generation_enabled",
            "value": True,
            "description": "Enable AI content generation",
            "category": "system",
        },
        {
            "key": "authenticity_threshold",
            "value": 0.75,
            "description": "Minimum authenticity score for content approval",
            "category": "brand",
        },
        {
            "key": "max_posts_per_day",
            "value": {"instagram": 3, "facebook": 4, "tiktok": 2, "youtube": 1, "google_posts": 2},
            "description": "Maximum posts per platform per day",
            "category": "schedule",
        },
        {
            "key": "posting_hours",
            "value": {"start": 8, "end": 21},
            "description": "Active posting hours (24h format)",
            "category": "schedule",
        },
        {
            "key": "notification_channels",
            "value": ["dashboard", "slack"],
            "description": "Active notification channels",
            "category": "notifications",
        },
        {
            "key": "timezone",
            "value": "America/Chicago",
            "description": "System timezone for scheduling",
            "category": "system",
        },
        {
            "key": "emergency_contacts",
            "value": Config.EMERGENCY_CONTACTS,
            "description": "Emergency contact emails",
            "category": "notifications",
        },
        {
            "key": "brand_colors",
            "value": Config.BRAND_COLORS,
            "description": "Brand color palette",
            "category": "brand",
        },
        {
            "key": "cajun_phrases_enabled",
            "value": True,
            "description": "Auto-enhance with Cajun phrases",
            "category": "content",
        },
        {
            "key": "auto_hashtags",
            "value": True,
            "description": "Auto-generate hashtags",
            "category": "content",
        },
        {
            "key": "ab_testing_enabled",
            "value": True,
            "description": "Enable A/B testing features",
            "category": "analytics",
        },
    ]

    logger.info("Creating default configurations...")

    for config in default_configs:
        config["updated_at"] = datetime.utcnow()
        config["updated_by"] = "system_init"

        await configs_collection.update_one({"key": config["key"]}, {"$set": config}, upsert=True)

    logger.info(f"Created {len(default_configs)} default configurations")


async def initialize_agent_states():
    """Initialize agent states in database"""
    from database import AgentRepository

    repo = AgentRepository()

    agents = [
        {
            "agent_name": "master_orchestrator",
            "status": "active",
            "health": "good",
            "description": "Central coordination hub",
        },
        {
            "agent_name": "content_generator",
            "status": "active",
            "health": "good",
            "description": "AI-powered content creation",
        },
        {
            "agent_name": "brand_voice_guardian",
            "status": "active",
            "health": "good",
            "description": "Brand voice validation",
        },
        {
            "agent_name": "analytics_agent",
            "status": "active",
            "health": "good",
            "description": "Performance analytics",
        },
        {
            "agent_name": "feedback_loop_agent",
            "status": "active",
            "health": "good",
            "description": "Continuous optimization",
        },
        {
            "agent_name": "scheduler_agent",
            "status": "active",
            "health": "good",
            "description": "Content scheduling",
        },
    ]

    logger.info("Initializing agent states...")

    for agent in agents:
        await repo.update_state(
            agent["agent_name"],
            {
                "status": agent["status"],
                "health": agent["health"],
                "description": agent["description"],
                "actions_today": 0,
                "errors_today": 0,
                "success_rate": 1.0,
            },
        )

    logger.info(f"Initialized {len(agents)} agent states")


async def create_sample_content():
    """Create sample content for testing"""
    from database import ContentRepository, ContentStatus

    repo = ContentRepository()

    sample_content = [
        {
            "text": "Good morning, cher! 🌅 The coffee's hot and the roux is bubbling. Come start your day with us at Randol's! Y'all come see us!",
            "content_type": "morning_greeting",
            "platforms": ["instagram", "facebook"],
            "hashtags": ["#GoodMorning", "#CajunFood", "#BreauxBridge", "#Louisiana"],
            "status": ContentStatus.APPROVED.value,
            "validation": {
                "authenticity_score": 0.92,
                "tone_compliance": True,
                "cultural_appropriateness": True,
                "brand_consistency": True,
            },
        },
        {
            "text": "Today's special: Gulf Shrimp Étouffée! 🦐 Cooked low and slow with our famous roux, just like Grand-mère taught us. That's some kinda good, y'all!",
            "content_type": "daily_special",
            "platforms": ["instagram", "facebook", "google_posts"],
            "hashtags": ["#DailySpecial", "#CajunFood", "#Etouffee", "#GulfShrimp"],
            "status": ContentStatus.APPROVED.value,
            "validation": {
                "authenticity_score": 0.95,
                "tone_compliance": True,
                "cultural_appropriateness": True,
                "brand_consistency": True,
            },
        },
        {
            "text": "🎵 Live zydeco tonight starting at 7pm! Bring your dancing shoes and an appetite. Laissez les bon temps rouler! 🎭",
            "content_type": "evening_event",
            "platforms": ["facebook", "instagram"],
            "hashtags": ["#LiveMusic", "#Zydeco", "#CajunMusic", "#BreauxBridge"],
            "status": ContentStatus.SCHEDULED.value,
            "scheduled_for": datetime.utcnow() + timedelta(hours=4),
            "validation": {
                "authenticity_score": 0.88,
                "tone_compliance": True,
                "cultural_appropriateness": True,
                "brand_consistency": True,
            },
        },
        {
            "text": "Fresh mudbugs just arrived from Louisiana waters! 🦞 Seasoned with our family's secret blend since 1973. Come get 'em while they're hot, cher!",
            "content_type": "crawfish_content",
            "platforms": ["instagram", "facebook", "tiktok"],
            "hashtags": ["#CrawfishSeason", "#Mudbugs", "#LouisianaCrawfish", "#CajunBoil"],
            "status": ContentStatus.APPROVED.value,
            "validation": {
                "authenticity_score": 0.94,
                "tone_compliance": True,
                "cultural_appropriateness": True,
                "brand_consistency": True,
            },
        },
        {
            "text": "Weekend vibes at Randol's! 🎉 Extended hours, live music, and our famous weekend crawfish boil. Reserve your table now - see y'all soon!",
            "content_type": "weekend_special",
            "platforms": ["facebook", "instagram"],
            "hashtags": ["#WeekendVibes", "#CrawfishBoil", "#LiveMusic", "#CajunFood"],
            "status": ContentStatus.DRAFT.value,
        },
    ]

    logger.info("Creating sample content...")

    content_ids = []
    for content in sample_content:
        content["created_by"] = "system_init"
        content_id = await repo.create(content)
        content_ids.append(content_id)

    logger.info(f"Created {len(sample_content)} sample content items")
    return content_ids


async def create_sample_analytics():
    """Create sample analytics data"""
    from database import AnalyticsRepository

    repo = AnalyticsRepository()

    logger.info("Creating sample analytics...")

    # Create 7 days of sample analytics
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")

        analytics = {
            "total_posts": 8 + (i % 3),
            "total_impressions": 15000 + (i * 500),
            "total_reach": 8000 + (i * 200),
            "total_engagement": 450 + (i * 20),
            "overall_engagement_rate": 0.035 + (i * 0.002),
            "performance_grade": "B" if i < 3 else "B+",
            "trend": "improving",
            "platforms": {
                "instagram": {
                    "total_posts": 3,
                    "total_impressions": 6000 + (i * 200),
                    "avg_engagement_rate": 0.042,
                },
                "facebook": {
                    "total_posts": 4,
                    "total_impressions": 7000 + (i * 250),
                    "avg_engagement_rate": 0.038,
                },
                "tiktok": {
                    "total_posts": 1,
                    "total_impressions": 2000 + (i * 50),
                    "avg_engagement_rate": 0.061,
                },
            },
            "content_type_performance": {
                "morning_greeting": 0.035,
                "daily_special": 0.042,
                "evening_event": 0.048,
                "crawfish_content": 0.055,
            },
        }

        await repo.save_daily(date, analytics)

    logger.info("Created 7 days of sample analytics")


async def send_initialization_notification():
    """Send notification about successful initialization"""
    from database import NotificationRepository

    repo = NotificationRepository()

    await repo.create(
        {
            "type": "success",
            "title": "System Initialized",
            "message": f"Randol's Marketing Platform initialized successfully at {datetime.utcnow().isoformat()}",
            "channels": ["dashboard"],
            "entity_type": "system",
            "entity_id": "init",
        }
    )

    logger.info("Initialization notification sent")


async def run_initialization(include_samples: bool = False):
    """Run complete database initialization"""
    logger.info("=" * 60)
    logger.info("Randol's Marketing Platform - Database Initialization")
    logger.info("=" * 60)

    # Check connection
    if not await check_connection():
        logger.error("Cannot proceed without database connection")
        return False

    try:
        # Create indexes
        await create_indexes()

        # Create default configurations
        await create_default_configs()

        # Initialize agent states
        await initialize_agent_states()

        # Create sample data if requested
        if include_samples:
            logger.info("Creating sample data...")
            await create_sample_content()
            await create_sample_analytics()

        # Send notification
        await send_initialization_notification()

        logger.info("=" * 60)
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.exception("Initialization failed")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Initialize Randol's Marketing Platform Database")
    parser.add_argument(
        "--samples", action="store_true", help="Include sample content and analytics data"
    )
    parser.add_argument("--check-only", action="store_true", help="Only check database connection")

    args = parser.parse_args()

    if args.check_only:
        success = asyncio.run(check_connection())
        sys.exit(0 if success else 1)

    try:
        success = asyncio.run(run_initialization(include_samples=args.samples))
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
