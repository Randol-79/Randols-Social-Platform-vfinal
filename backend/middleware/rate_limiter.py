"""
Rate Limiting Middleware for Flask
Implements configurable rate limiting using Flask-Limiter
"""

import os
from functools import wraps
from typing import Callable, Optional

from flask import Flask, request, jsonify, g
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger("rate_limiter")

# Try to import Flask-Limiter
LIMITER_AVAILABLE = False
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    logger.warning("flask-limiter not installed, rate limiting disabled")


class RateLimiter:
    """
    Rate limiter wrapper with configuration from environment.
    Falls back gracefully when flask-limiter is not available.
    """

    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.limiter = None
        self.enabled = Config.RATE_LIMIT_ENABLED if hasattr(Config, 'RATE_LIMIT_ENABLED') else True

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize rate limiter with Flask app"""
        self.app = app

        if not self.enabled:
            logger.info("Rate limiting disabled by configuration")
            return

        if not LIMITER_AVAILABLE:
            logger.warning("Rate limiting unavailable (flask-limiter not installed)")
            return

        # Get configuration
        per_minute = getattr(Config, 'RATE_LIMIT_PER_MINUTE', 60)
        per_hour = getattr(Config, 'RATE_LIMIT_PER_HOUR', 1000)

        # Configure storage backend
        redis_url = self._get_redis_url()

        try:
            self.limiter = Limiter(
                app=app,
                key_func=self._get_request_key,
                default_limits=[f"{per_hour} per hour", f"{per_minute} per minute"],
                storage_uri=redis_url or "memory://",
                strategy="fixed-window",
                headers_enabled=True,
                swallow_errors=True,  # Don't break app if rate limiting fails
            )

            # Add error handler
            @app.errorhandler(429)
            def rate_limit_exceeded(e):
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": str(e.description),
                    "retry_after": getattr(e, 'retry_after', 60)
                }), 429

            logger.info(f"Rate limiter initialized: {per_minute}/min, {per_hour}/hour")

        except Exception as e:
            logger.error(f"Failed to initialize rate limiter: {e}")
            self.limiter = None

    def _get_redis_url(self) -> Optional[str]:
        """Get Redis URL for rate limit storage"""
        redis_url = getattr(Config, 'REDIS_URL', None)
        if redis_url:
            return redis_url

        redis_host = getattr(Config, 'REDIS_HOST', 'localhost')
        redis_port = getattr(Config, 'REDIS_PORT', 6379)
        redis_password = getattr(Config, 'REDIS_PASSWORD', None)

        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}/1"
        return f"redis://{redis_host}:{redis_port}/1"

    def _get_request_key(self) -> str:
        """Get the key for rate limiting (IP or API key)"""
        # Check for API key first
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if api_key:
            return f"api_key:{api_key}"

        # Fall back to IP address
        return get_remote_address() if LIMITER_AVAILABLE else request.remote_addr

    def limit(self, limit_string: str):
        """
        Decorator to apply custom rate limit to a route.

        Usage:
            @rate_limiter.limit("10 per minute")
            def my_route():
                pass
        """
        def decorator(f: Callable) -> Callable:
            if self.limiter:
                return self.limiter.limit(limit_string)(f)
            return f
        return decorator

    def exempt(self):
        """
        Decorator to exempt a route from rate limiting.

        Usage:
            @rate_limiter.exempt()
            def health_check():
                pass
        """
        def decorator(f: Callable) -> Callable:
            if self.limiter:
                return self.limiter.exempt(f)
            return f
        return decorator

    def shared_limit(self, limit_string: str, scope: str):
        """
        Decorator for shared rate limits across multiple routes.

        Usage:
            @rate_limiter.shared_limit("100 per hour", "content_api")
            def create_content():
                pass
        """
        def decorator(f: Callable) -> Callable:
            if self.limiter:
                return self.limiter.shared_limit(limit_string, scope)(f)
            return f
        return decorator


# Pre-defined rate limit configurations
class RateLimitPresets:
    """Common rate limit configurations"""

    # Public endpoints
    PUBLIC_READ = "100 per minute"
    PUBLIC_WRITE = "20 per minute"

    # Authenticated endpoints
    AUTH_READ = "200 per minute"
    AUTH_WRITE = "50 per minute"

    # Admin endpoints
    ADMIN = "30 per minute"

    # AI/LLM endpoints (expensive operations)
    AI_GENERATION = "10 per minute"
    AI_VALIDATION = "30 per minute"

    # Webhook endpoints
    WEBHOOK = "60 per minute"

    # Health/status endpoints
    HEALTH = "120 per minute"


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def init_rate_limiter(app: Flask) -> RateLimiter:
    """Initialize the global rate limiter"""
    global _rate_limiter
    _rate_limiter = RateLimiter(app)
    return _rate_limiter


def get_rate_limiter() -> Optional[RateLimiter]:
    """Get the global rate limiter instance"""
    return _rate_limiter


# Convenience decorators for common patterns
def rate_limit(limit_string: str):
    """
    Convenience decorator for rate limiting.

    Usage:
        @rate_limit("10 per minute")
        def my_route():
            pass
    """
    def decorator(f: Callable) -> Callable:
        if _rate_limiter and _rate_limiter.limiter:
            return _rate_limiter.limiter.limit(limit_string)(f)
        return f
    return decorator


def rate_limit_exempt():
    """
    Convenience decorator to exempt from rate limiting.

    Usage:
        @rate_limit_exempt()
        def health_check():
            pass
    """
    def decorator(f: Callable) -> Callable:
        if _rate_limiter and _rate_limiter.limiter:
            return _rate_limiter.limiter.exempt(f)
        return f
    return decorator
