"""
Configuration settings for Randol's Agentic Marketing Platform
Environment variables and API keys management
"""

import os
from datetime import datetime
from typing import Any, Dict, List


class Config:
    # ============================================
    # API KEYS
    # ============================================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    CANVA_API_KEY = os.getenv("CANVA_API_KEY", "")

    # Social Media API Keys
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    GOOGLE_POSTS_API_KEY = os.getenv("GOOGLE_POSTS_API_KEY", "")

    # ============================================
    # DATABASE CONFIGURATION
    # ============================================
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/randols_marketing")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    # ============================================
    # RESTAURANT INFORMATION
    # ============================================
    RESTAURANT_NAME = "Randol's Restaurant"
    RESTAURANT_LOCATION = "Breaux Bridge, Louisiana"
    RESTAURANT_ADDRESS = "2320 Kaliste Saloom Rd, Lafayette, LA 70508"
    RESTAURANT_PHONE = "(337) 332-4648"
    RESTAURANT_ESTABLISHED = "1973"
    RESTAURANT_WEBSITE = "https://randols.com"

    # Restaurant Hours
    RESTAURANT_HOURS = {
        "monday": {"open": "11:00", "close": "21:00"},
        "tuesday": {"open": "11:00", "close": "21:00"},
        "wednesday": {"open": "11:00", "close": "21:00"},
        "thursday": {"open": "11:00", "close": "21:00"},
        "friday": {"open": "11:00", "close": "22:00"},
        "saturday": {"open": "11:00", "close": "22:00"},
        "sunday": {"open": "11:00", "close": "21:00"},
    }

    # ============================================
    # BRAND GUIDELINES
    # ============================================
    BRAND_COLORS = {
        "primary": "#C0152F",  # Deep Cajun red
        "secondary": "#A84B2F",  # Warm brown (roux color)
        "accent": "#32808D",  # Bayou teal
        "gold": "#D4AF37",  # Louisiana gold
        "cream": "#F5F0E6",  # Warm cream
        "dark": "#2C1810",  # Rich dark brown
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
    }

    BRAND_FONTS = {
        "heading": "Playfair Display",
        "body": "Source Sans Pro",
        "accent": "Dancing Script",
    }

    # ============================================
    # SCHEDULING CONFIGURATION
    # ============================================
    POSTING_SCHEDULE = {
        "monday": {"morning": "08:00", "lunch": "11:30", "evening": "17:00"},
        "tuesday": {"morning": "08:30", "lunch": "11:30", "evening": "17:30"},
        "wednesday": {"morning": "08:00", "lunch": "11:30", "evening": "17:00"},
        "thursday": {"morning": "08:30", "lunch": "11:30", "evening": "17:30"},
        "friday": {"morning": "09:00", "lunch": "12:00", "evening": "18:00"},
        "saturday": {"morning": "09:30", "lunch": "12:00", "evening": "19:00"},
        "sunday": {"morning": "10:00", "lunch": "12:30", "evening": "18:30"},
    }

    # ============================================
    # CONTENT LIMITS
    # ============================================
    CONTENT_LIMITS = {
        "instagram_caption": 2200,
        "instagram_bio": 150,
        "instagram_hashtags": 30,
        "facebook_post": 63206,
        "facebook_comment": 8000,
        "twitter_tweet": 280,
        "tiktok_caption": 150,
        "tiktok_hashtags": 20,
        "youtube_title": 100,
        "youtube_description": 5000,
        "google_posts": 1500,
    }

    # ============================================
    # PLATFORM CONFIGURATIONS
    # ============================================
    PLATFORM_CONFIGS = {
        "instagram": {
            "max_caption_length": 2200,
            "optimal_image_size": {"width": 1080, "height": 1080},
            "story_size": {"width": 1080, "height": 1920},
            "reel_size": {"width": 1080, "height": 1920},
            "hashtag_limit": 30,
            "posting_frequency": "daily",
            "best_times": ["09:00", "12:00", "18:00"],
        },
        "facebook": {
            "max_post_length": 63206,
            "optimal_image_size": {"width": 1200, "height": 630},
            "cover_size": {"width": 820, "height": 312},
            "hashtag_limit": 10,
            "posting_frequency": "2x_daily",
            "best_times": ["08:30", "13:00", "19:00"],
        },
        "tiktok": {
            "max_caption_length": 150,
            "video_length": {"min": 15, "max": 180},
            "optimal_size": {"width": 1080, "height": 1920},
            "hashtag_limit": 20,
            "posting_frequency": "daily",
            "best_times": ["15:00", "19:00", "21:00"],
        },
        "youtube": {
            "max_title_length": 100,
            "max_description_length": 5000,
            "optimal_thumbnail_size": {"width": 1280, "height": 720},
            "hashtag_limit": 15,
            "posting_frequency": "weekly",
            "best_times": ["14:00", "17:00"],
        },
        "google_posts": {
            "max_post_length": 1500,
            "optimal_image_size": {"width": 1200, "height": 900},
            "posting_frequency": "daily",
            "best_times": ["10:00", "14:00"],
        },
    }

    # ============================================
    # WEBHOOK URLS
    # ============================================
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

    # ============================================
    # EXTERNAL APIS
    # ============================================
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    BREAUX_BRIDGE_LAT = 30.2741
    BREAUX_BRIDGE_LON = -91.8992

    LAFAYETTE_EVENTS_API = os.getenv("LAFAYETTE_EVENTS_API", "")

    # ============================================
    # PERFORMANCE THRESHOLDS
    # ============================================
    ENGAGEMENT_THRESHOLDS = {
        "excellent": 0.06,  # 6%+ engagement rate
        "good": 0.04,  # 4%+ engagement rate
        "average": 0.025,  # 2.5%+ engagement rate
        "poor": 0.015,  # Below 1.5% needs attention
    }

    AUTHENTICITY_THRESHOLD = 0.75  # Minimum authenticity score for auto-approval

    SENTIMENT_THRESHOLDS = {"positive": 0.6, "neutral": 0.4, "negative": 0.3}

    # ============================================
    # EMERGENCY CONTACTS
    # ============================================
    EMERGENCY_CONTACTS = [
        {"name": "Manager", "email": "manager@randols.com", "phone": "(337) 332-4648"},
        {"name": "Marketing", "email": "marketing@randols.com"},
    ]

    # ============================================
    # SEASONAL EVENTS
    # ============================================
    SEASONAL_EVENTS = {
        "crawfish_season": {
            "start_month": 3,
            "end_month": 6,
            "keywords": ["crawfish", "mudbugs", "boil", "fresh catch"],
            "content_boost": 1.5,
        },
        "mardi_gras": {
            "approximate_date": "february-march",
            "keywords": ["mardi gras", "carnival", "king cake", "celebration"],
            "content_boost": 2.0,
        },
        "festival_season": {
            "start_month": 4,
            "end_month": 10,
            "keywords": ["festival", "live music", "dancing", "outdoor"],
            "content_boost": 1.3,
        },
        "holiday_season": {
            "start_month": 11,
            "end_month": 12,
            "keywords": ["holiday", "family", "tradition", "celebration"],
            "content_boost": 1.4,
        },
    }

    # ============================================
    # METHODS
    # ============================================

    @classmethod
    def get_platform_config(cls, platform: str) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        return cls.PLATFORM_CONFIGS.get(platform, {})

    @classmethod
    def get_current_season(cls) -> Dict[str, Any]:
        """Get current seasonal context"""
        month = datetime.now().month

        for season_name, season_data in cls.SEASONAL_EVENTS.items():
            if "start_month" in season_data and "end_month" in season_data:
                if season_data["start_month"] <= month <= season_data["end_month"]:
                    return {
                        "season": season_name,
                        "keywords": season_data["keywords"],
                        "content_boost": season_data["content_boost"],
                    }

        return {
            "season": "regular",
            "keywords": ["authentic", "tradition", "family", "Louisiana"],
            "content_boost": 1.0,
        }

    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate configuration settings"""
        validation = {
            "openai_configured": bool(cls.OPENAI_API_KEY),
            "database_configured": "localhost" not in cls.MONGODB_URI or os.getenv("MONGODB_URI"),
            "redis_configured": bool(cls.REDIS_HOST),
            "social_media_configured": any(
                [bool(cls.INSTAGRAM_ACCESS_TOKEN), bool(cls.FACEBOOK_ACCESS_TOKEN)]
            ),
            "webhooks_configured": bool(cls.SLACK_WEBHOOK_URL),
            "weather_configured": bool(cls.WEATHER_API_KEY),
        }

        return validation

    @classmethod
    def get_config_status(cls) -> Dict[str, Any]:
        """Get configuration status for dashboard"""
        validation = cls.validate_config()

        return {
            "all_configured": all(validation.values()),
            "validation": validation,
            "environment": os.getenv("FLASK_ENV", "development"),
            "version": "1.0.0",
        }

    @classmethod
    def is_restaurant_open(cls) -> bool:
        """Check if restaurant is currently open"""
        now = datetime.now()
        day = now.strftime("%A").lower()
        current_time = now.strftime("%H:%M")

        hours = cls.RESTAURANT_HOURS.get(day, {})
        if hours:
            return hours["open"] <= current_time <= hours["close"]
        return False

    @classmethod
    def get_next_posting_time(cls, platform: str = "instagram") -> str:
        """Get next optimal posting time"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        day = now.strftime("%A").lower()

        platform_config = cls.PLATFORM_CONFIGS.get(platform, {})
        best_times = platform_config.get("best_times", ["09:00", "12:00", "18:00"])

        for time in best_times:
            if time > current_time:
                return time

        return best_times[0]  # Return first time for next day


# Singleton instance
config = Config()
