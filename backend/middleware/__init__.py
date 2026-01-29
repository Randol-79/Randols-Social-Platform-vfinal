"""
Middleware Package
==================
Authentication, rate limiting, and request handling middleware.
"""

from .auth import (
    require_auth,
    require_admin,
    rate_limit,
    authenticate_request,
    JWTManager,
    validate_api_key,
    get_api_key_from_request,
    setup_cors,
    generate_api_key,
    AuthConfig,
)

from .rate_limiter import (
    RateLimiter,
    RateLimitPresets,
    init_rate_limiter,
    get_rate_limiter,
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
