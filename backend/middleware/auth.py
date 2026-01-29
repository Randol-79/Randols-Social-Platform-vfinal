"""
Authentication and Authorization Middleware
==========================================
Provides API key validation, JWT authentication, and rate limiting.
"""

import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional

import jwt
import redis
from flask import current_app, g, jsonify, request

# ============================================
# Configuration
# ============================================


class AuthConfig:
    """Authentication configuration."""

    # API Key settings
    API_KEY_HEADER = "X-API-Key"
    API_KEY_QUERY_PARAM = "api_key"

    # JWT settings
    JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = 24
    JWT_REFRESH_EXPIRY_DAYS = 7

    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_DEFAULT = 100  # requests per minute
    RATE_LIMIT_WINDOW = 60  # seconds

    # Allowed API keys (in production, store in secure vault)
    VALID_API_KEYS = set(
        filter(
            None,
            [
                os.getenv("API_KEY"),
                os.getenv("API_KEY_SECONDARY"),
                os.getenv("ADMIN_API_KEY"),
            ],
        )
    )

    # Admin API keys (have elevated permissions)
    ADMIN_API_KEYS = set(
        filter(
            None,
            [
                os.getenv("ADMIN_API_KEY"),
            ],
        )
    )

    # Public endpoints (no auth required)
    PUBLIC_ENDPOINTS = [
        "/api/v1/health",
        "/api/v1/status",
        "/api/v1/docs",
        "/",
    ]

    # Admin-only endpoints
    ADMIN_ENDPOINTS = [
        "/api/v1/admin/",
        "/api/v1/agents/*/restart",
    ]


# ============================================
# Rate Limiter
# ============================================


class RateLimiter:
    """Token bucket rate limiter using Redis."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self._local_cache: Dict[str, Dict[str, Any]] = {}

    def is_allowed(
        self,
        key: str,
        limit: int = AuthConfig.RATE_LIMIT_DEFAULT,
        window: int = AuthConfig.RATE_LIMIT_WINDOW,
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.

        Returns:
            Tuple of (allowed: bool, info: dict with remaining, reset_at)
        """
        if not AuthConfig.RATE_LIMIT_ENABLED:
            return True, {"remaining": -1, "reset_at": None}

        now = time.time()

        # Use Redis if available
        if self.redis:
            return self._redis_rate_limit(key, limit, window, now)

        # Fallback to local cache (not recommended for production)
        return self._local_rate_limit(key, limit, window, now)

    def _redis_rate_limit(
        self, key: str, limit: int, window: int, now: float
    ) -> tuple[bool, Dict[str, Any]]:
        """Redis-based rate limiting with sliding window."""
        redis_key = f"ratelimit:{key}"

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(redis_key, 0, now - window)
        pipe.zadd(redis_key, {str(now): now})
        pipe.zcount(redis_key, now - window, now)
        pipe.expire(redis_key, window)

        results = pipe.execute()
        request_count = results[2]

        remaining = max(0, limit - request_count)
        reset_at = now + window

        return request_count <= limit, {
            "remaining": remaining,
            "reset_at": int(reset_at),
            "limit": limit,
        }

    def _local_rate_limit(
        self, key: str, limit: int, window: int, now: float
    ) -> tuple[bool, Dict[str, Any]]:
        """Local in-memory rate limiting (for development only)."""
        if key not in self._local_cache:
            self._local_cache[key] = {"requests": [], "window_start": now}

        cache = self._local_cache[key]

        # Clean old requests
        cache["requests"] = [t for t in cache["requests"] if t > now - window]

        # Check limit
        if len(cache["requests"]) >= limit:
            return False, {
                "remaining": 0,
                "reset_at": int(now + window),
                "limit": limit,
            }

        # Add request
        cache["requests"].append(now)

        return True, {
            "remaining": limit - len(cache["requests"]),
            "reset_at": int(now + window),
            "limit": limit,
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        redis_client = None
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                redis_client = redis.from_url(redis_url)
                redis_client.ping()
            except Exception:
                redis_client = None
        _rate_limiter = RateLimiter(redis_client)
    return _rate_limiter


# ============================================
# JWT Token Management
# ============================================


class JWTManager:
    """JWT token generation and validation."""

    @staticmethod
    def generate_token(
        user_id: str, role: str = "user", extra_claims: Optional[Dict] = None
    ) -> str:
        """Generate a JWT access token."""
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "role": role,
            "iat": now,
            "exp": now + timedelta(hours=AuthConfig.JWT_EXPIRY_HOURS),
            "type": "access",
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(payload, AuthConfig.JWT_SECRET, algorithm=AuthConfig.JWT_ALGORITHM)

    @staticmethod
    def generate_refresh_token(user_id: str) -> str:
        """Generate a JWT refresh token."""
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(days=AuthConfig.JWT_REFRESH_EXPIRY_DAYS),
            "type": "refresh",
        }
        return jwt.encode(payload, AuthConfig.JWT_SECRET, algorithm=AuthConfig.JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token, AuthConfig.JWT_SECRET, algorithms=[AuthConfig.JWT_ALGORITHM]
            )
            if payload.get("type") != token_type:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token."""
        payload = JWTManager.verify_token(refresh_token, "refresh")
        if not payload:
            return None

        return JWTManager.generate_token(payload["sub"], payload.get("role", "user"))


# ============================================
# API Key Validation
# ============================================


def validate_api_key(api_key: str) -> tuple[bool, bool]:
    """
    Validate API key.

    Returns:
        Tuple of (is_valid: bool, is_admin: bool)
    """
    if not api_key:
        return False, False

    # Constant-time comparison to prevent timing attacks
    is_valid = any(
        hmac.compare_digest(api_key, valid_key) for valid_key in AuthConfig.VALID_API_KEYS
    )

    is_admin = any(
        hmac.compare_digest(api_key, admin_key) for admin_key in AuthConfig.ADMIN_API_KEYS
    )

    return is_valid, is_admin


def get_api_key_from_request() -> Optional[str]:
    """Extract API key from request headers or query params."""
    # Check header first
    api_key = request.headers.get(AuthConfig.API_KEY_HEADER)
    if api_key:
        return api_key

    # Check query parameter
    api_key = request.args.get(AuthConfig.API_KEY_QUERY_PARAM)
    if api_key:
        return api_key

    # Check Authorization header (Bearer token style)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


# ============================================
# Authentication Decorators
# ============================================


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication (API key or JWT)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if endpoint is public
        if any(request.path.startswith(ep) for ep in AuthConfig.PUBLIC_ENDPOINTS):
            return f(*args, **kwargs)

        # Try API key first
        api_key = get_api_key_from_request()
        if api_key:
            is_valid, is_admin = validate_api_key(api_key)
            if is_valid:
                g.auth_method = "api_key"
                g.is_admin = is_admin
                return f(*args, **kwargs)

        # Try JWT token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = JWTManager.verify_token(token)
            if payload:
                g.auth_method = "jwt"
                g.user_id = payload.get("sub")
                g.role = payload.get("role", "user")
                g.is_admin = payload.get("role") == "admin"
                return f(*args, **kwargs)

        return (
            jsonify(
                {
                    "error": "Authentication required",
                    "message": "Please provide a valid API key or JWT token",
                }
            ),
            401,
        )

    return decorated


def require_admin(f: Callable) -> Callable:
    """Decorator to require admin privileges."""

    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if not getattr(g, "is_admin", False):
            return (
                jsonify(
                    {
                        "error": "Admin access required",
                        "message": "This endpoint requires admin privileges",
                    }
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated


def rate_limit(
    limit: int = AuthConfig.RATE_LIMIT_DEFAULT,
    window: int = AuthConfig.RATE_LIMIT_WINDOW,
    key_func: Optional[Callable] = None,
) -> Callable:
    """Decorator to apply rate limiting."""

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Determine rate limit key
            if key_func:
                rate_key = key_func()
            else:
                # Default: use IP + endpoint
                rate_key = f"{request.remote_addr}:{request.endpoint}"

            limiter = get_rate_limiter()
            allowed, info = limiter.is_allowed(rate_key, limit, window)

            # Add rate limit headers
            response_headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info.get("reset_at", "")),
            }

            if not allowed:
                response = jsonify(
                    {
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {limit} per {window} seconds",
                        "retry_after": info.get("reset_at", 0) - int(time.time()),
                    }
                )
                response.status_code = 429
                for key, value in response_headers.items():
                    response.headers[key] = value
                return response

            # Call the actual function
            response = f(*args, **kwargs)

            # Add headers to response
            if hasattr(response, "headers"):
                for key, value in response_headers.items():
                    response.headers[key] = value

            return response

        return decorated

    return decorator


# ============================================
# Request Authentication Hook
# ============================================


def authenticate_request():
    """
    Flask before_request hook for authentication.

    Use with: app.before_request(authenticate_request)
    """
    # Skip for public endpoints
    if any(request.path.startswith(ep) for ep in AuthConfig.PUBLIC_ENDPOINTS):
        g.authenticated = False
        g.is_admin = False
        return None

    # Skip for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return None

    # Try to authenticate
    api_key = get_api_key_from_request()
    if api_key:
        is_valid, is_admin = validate_api_key(api_key)
        if is_valid:
            g.authenticated = True
            g.auth_method = "api_key"
            g.is_admin = is_admin
            return None

    # Try JWT
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = JWTManager.verify_token(token)
        if payload:
            g.authenticated = True
            g.auth_method = "jwt"
            g.user_id = payload.get("sub")
            g.role = payload.get("role", "user")
            g.is_admin = payload.get("role") == "admin"
            return None

    # No valid authentication found
    # For now, allow unauthenticated access but mark it
    g.authenticated = False
    g.is_admin = False

    # Uncomment to enforce authentication:
    # return jsonify({'error': 'Authentication required'}), 401

    return None


# ============================================
# CORS Helper
# ============================================


def setup_cors(app):
    """Configure CORS for the Flask app."""
    from flask_cors import CORS

    allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")

    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Request-ID"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )


# ============================================
# Utility Functions
# ============================================


def generate_api_key() -> str:
    """Generate a new API key."""
    return f"rnd_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()
