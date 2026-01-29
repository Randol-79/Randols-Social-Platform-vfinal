"""
Middleware Package
==================
Authentication, rate limiting, and request handling middleware.
"""

from .auth import (
    AuthConfig,
    JWTManager,
    authenticate_request,
    generate_api_key,
    get_api_key_from_request,
    rate_limit,
    require_admin,
    require_auth,
    setup_cors,
    validate_api_key,
)
from .rate_limiter import (
    RateLimiter,
    RateLimitPresets,
    get_rate_limiter,
    init_rate_limiter,
    rate_limit_exempt,
)

__all__ = [
    "require_auth",
    "require_admin",
    "rate_limit",
    "authenticate_request",
    "JWTManager",
    "validate_api_key",
    "get_api_key_from_request",
    "setup_cors",
    "generate_api_key",
    "AuthConfig",
    "RateLimiter",
    "RateLimitPresets",
    "init_rate_limiter",
    "get_rate_limiter",
    "rate_limit_exempt",
]
