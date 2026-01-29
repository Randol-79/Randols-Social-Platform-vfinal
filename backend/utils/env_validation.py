"""
Environment Configuration Validation
=====================================
Validates required environment variables and provides sensible defaults.
Run at application startup to fail fast on misconfigurations.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class EnvVarType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    URL = "url"
    LIST = "list"


@dataclass
class EnvVar:
    """Environment variable definition."""

    name: str
    var_type: EnvVarType = EnvVarType.STRING
    required: bool = False
    default: Any = None
    description: str = ""
    validator: Optional[callable] = None
    sensitive: bool = False


@dataclass
class ValidationResult:
    """Result of environment validation."""

    valid: bool
    missing: List[str] = field(default_factory=list)
    invalid: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


# ============================================
# Environment Variable Definitions
# ============================================

ENVIRONMENT_VARIABLES = [
    # ===================
    # Core Configuration
    # ===================
    EnvVar(
        name="FLASK_ENV",
        default="production",
        description="Flask environment (development, staging, production)",
    ),
    EnvVar(
        name="FLASK_DEBUG",
        var_type=EnvVarType.BOOLEAN,
        default=False,
        description="Enable Flask debug mode",
    ),
    EnvVar(
        name="SECRET_KEY",
        required=True,
        sensitive=True,
        description="Flask secret key for session signing",
    ),
    # ===================
    # Database
    # ===================
    EnvVar(
        name="MONGODB_URI",
        var_type=EnvVarType.URL,
        required=True,
        sensitive=True,
        description="MongoDB connection string",
    ),
    EnvVar(
        name="MONGODB_DATABASE", default="randols_marketing", description="MongoDB database name"
    ),
    # ===================
    # Cache (Redis)
    # ===================
    EnvVar(
        name="REDIS_URL",
        var_type=EnvVarType.URL,
        default=None,
        description="Redis connection URL (optional)",
    ),
    EnvVar(name="REDIS_HOST", default="localhost", description="Redis host"),
    EnvVar(name="REDIS_PORT", var_type=EnvVarType.INTEGER, default=6379, description="Redis port"),
    # ===================
    # OpenAI / AI
    # ===================
    EnvVar(
        name="OPENAI_API_KEY",
        required=True,
        sensitive=True,
        description="OpenAI API key for content generation",
    ),
    EnvVar(name="OPENAI_MODEL", default="gpt-4-turbo-preview", description="OpenAI model to use"),
    EnvVar(
        name="OPENAI_MAX_TOKENS",
        var_type=EnvVarType.INTEGER,
        default=1000,
        description="Maximum tokens for AI responses",
    ),
    # ===================
    # Social Media APIs
    # ===================
    EnvVar(
        name="INSTAGRAM_ACCESS_TOKEN",
        sensitive=True,
        description="Instagram Graph API access token",
    ),
    EnvVar(name="INSTAGRAM_BUSINESS_ID", description="Instagram Business Account ID"),
    EnvVar(name="FACEBOOK_ACCESS_TOKEN", sensitive=True, description="Facebook Page access token"),
    EnvVar(name="FACEBOOK_PAGE_ID", description="Facebook Page ID"),
    EnvVar(name="TIKTOK_ACCESS_TOKEN", sensitive=True, description="TikTok API access token"),
    EnvVar(name="YOUTUBE_API_KEY", sensitive=True, description="YouTube Data API key"),
    EnvVar(name="YOUTUBE_CHANNEL_ID", description="YouTube Channel ID"),
    EnvVar(
        name="GOOGLE_MY_BUSINESS_API_KEY", sensitive=True, description="Google My Business API key"
    ),
    # ===================
    # Authentication
    # ===================
    EnvVar(
        name="API_KEY",
        required=True,
        sensitive=True,
        description="Primary API key for authentication",
    ),
    EnvVar(name="API_KEY_SECONDARY", sensitive=True, description="Secondary API key (backup)"),
    EnvVar(name="ADMIN_API_KEY", sensitive=True, description="Admin API key for elevated access"),
    EnvVar(name="JWT_SECRET", sensitive=True, description="JWT signing secret"),
    # ===================
    # Rate Limiting
    # ===================
    EnvVar(
        name="RATE_LIMIT_ENABLED",
        var_type=EnvVarType.BOOLEAN,
        default=True,
        description="Enable API rate limiting",
    ),
    EnvVar(
        name="RATE_LIMIT_DEFAULT",
        var_type=EnvVarType.INTEGER,
        default=100,
        description="Default requests per minute",
    ),
    # ===================
    # CORS
    # ===================
    EnvVar(
        name="CORS_ORIGINS",
        var_type=EnvVarType.LIST,
        default="*",
        description="Allowed CORS origins (comma-separated)",
    ),
    # ===================
    # Notifications
    # ===================
    EnvVar(
        name="SLACK_WEBHOOK_URL",
        var_type=EnvVarType.URL,
        description="Slack webhook for notifications",
    ),
    EnvVar(
        name="DISCORD_WEBHOOK_URL",
        var_type=EnvVarType.URL,
        description="Discord webhook for notifications",
    ),
    EnvVar(
        name="EMAIL_NOTIFICATIONS_ENABLED",
        var_type=EnvVarType.BOOLEAN,
        default=False,
        description="Enable email notifications",
    ),
    # ===================
    # Business Settings
    # ===================
    EnvVar(
        name="RESTAURANT_NAME",
        default="Randol's Restaurant",
        description="Restaurant name for branding",
    ),
    EnvVar(
        name="RESTAURANT_TIMEZONE", default="America/Chicago", description="Restaurant timezone"
    ),
    EnvVar(
        name="AUTHENTICITY_THRESHOLD",
        var_type=EnvVarType.FLOAT,
        default=0.75,
        description="Minimum Cajun authenticity score",
    ),
    # ===================
    # Feature Flags
    # ===================
    EnvVar(
        name="MOCK_MODE",
        var_type=EnvVarType.BOOLEAN,
        default=False,
        description="Enable mock mode (no actual API calls)",
    ),
    EnvVar(
        name="FEATURE_AI_GENERATION",
        var_type=EnvVarType.BOOLEAN,
        default=True,
        description="Enable AI content generation",
    ),
    EnvVar(
        name="FEATURE_AUTO_POSTING",
        var_type=EnvVarType.BOOLEAN,
        default=True,
        description="Enable automatic posting",
    ),
    EnvVar(
        name="FEATURE_ANALYTICS",
        var_type=EnvVarType.BOOLEAN,
        default=True,
        description="Enable analytics collection",
    ),
]


# ============================================
# Value Parsers
# ============================================


def parse_boolean(value: str) -> bool:
    """Parse boolean from string."""
    return value.lower() in ("true", "1", "yes", "on", "enabled")


def parse_list(value: str, separator: str = ",") -> List[str]:
    """Parse list from comma-separated string."""
    if not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]


def parse_value(value: str, var_type: EnvVarType) -> Any:
    """Parse value based on type."""
    if value is None:
        return None

    parsers = {
        EnvVarType.STRING: str,
        EnvVarType.INTEGER: int,
        EnvVarType.FLOAT: float,
        EnvVarType.BOOLEAN: parse_boolean,
        EnvVarType.URL: str,
        EnvVarType.LIST: parse_list,
    }

    parser = parsers.get(var_type, str)
    return parser(value)


# ============================================
# Validators
# ============================================


def validate_url(value: str) -> bool:
    """Validate URL format."""
    if not value:
        return True
    return value.startswith(("http://", "https://", "mongodb://", "mongodb+srv://", "redis://"))


def validate_port(value: int) -> bool:
    """Validate port number."""
    return 1 <= value <= 65535


def validate_percentage(value: float) -> bool:
    """Validate percentage (0-1)."""
    return 0 <= value <= 1


# ============================================
# Main Validation Function
# ============================================


def validate_environment(
    env_vars: List[EnvVar] = None, strict: bool = False, log_config: bool = False
) -> ValidationResult:
    """
    Validate environment configuration.

    Args:
        env_vars: List of environment variable definitions
        strict: If True, exit on validation failure
        log_config: If True, print non-sensitive config values

    Returns:
        ValidationResult with validation status and parsed config
    """
    if env_vars is None:
        env_vars = ENVIRONMENT_VARIABLES

    result = ValidationResult(valid=True)

    for var in env_vars:
        raw_value = os.getenv(var.name)

        # Check if required variable is missing
        if var.required and not raw_value:
            result.missing.append(var.name)
            result.valid = False
            continue

        # Use default if not set
        if raw_value is None:
            value = var.default
        else:
            # Parse value
            try:
                value = parse_value(raw_value, var.var_type)
            except (ValueError, TypeError) as e:
                result.invalid[var.name] = f"Invalid {var.var_type.value}: {str(e)}"
                result.valid = False
                continue

        # Run custom validator
        if var.validator and value is not None:
            try:
                if not var.validator(value):
                    result.invalid[var.name] = "Custom validation failed"
                    result.valid = False
                    continue
            except Exception as e:
                result.invalid[var.name] = f"Validator error: {str(e)}"
                result.valid = False
                continue

        # URL validation
        if var.var_type == EnvVarType.URL and value:
            if not validate_url(value):
                result.invalid[var.name] = "Invalid URL format"
                result.valid = False
                continue

        # Store parsed value
        result.config[var.name] = value

    # Generate warnings for optional but recommended variables
    recommended = ["REDIS_URL", "SLACK_WEBHOOK_URL", "JWT_SECRET"]
    for var_name in recommended:
        if var_name not in result.config or result.config[var_name] is None:
            result.warnings.append(f"{var_name} is not set (recommended for production)")

    # Log configuration if requested
    if log_config:
        print("\n" + "=" * 50)
        print("ENVIRONMENT CONFIGURATION")
        print("=" * 50)
        for var in env_vars:
            value = result.config.get(var.name)
            if var.sensitive and value:
                display_value = f"{value[:4]}...{value[-4:]}" if len(str(value)) > 8 else "***"
            else:
                display_value = value
            status = "✓" if var.name in result.config else "✗"
            print(f"{status} {var.name}: {display_value}")
        print("=" * 50 + "\n")

    # Handle strict mode
    if strict and not result.valid:
        print("\n❌ ENVIRONMENT VALIDATION FAILED\n")

        if result.missing:
            print("Missing required variables:")
            for var_name in result.missing:
                print(f"  - {var_name}")

        if result.invalid:
            print("\nInvalid variables:")
            for var_name, error in result.invalid.items():
                print(f"  - {var_name}: {error}")

        print("\nPlease set the required environment variables and try again.")
        sys.exit(1)

    return result


def get_config(key: str, default: Any = None) -> Any:
    """Get a validated config value."""
    result = validate_environment()
    return result.config.get(key, default)


# ============================================
# Quick Access Functions
# ============================================


def is_production() -> bool:
    """Check if running in production."""
    return os.getenv("FLASK_ENV", "production").lower() == "production"


def is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return parse_boolean(os.getenv("MOCK_MODE", "false"))


def get_mongodb_uri() -> str:
    """Get MongoDB URI."""
    return os.getenv("MONGODB_URI", "")


def get_redis_url() -> Optional[str]:
    """Get Redis URL."""
    return os.getenv("REDIS_URL")


def get_openai_key() -> str:
    """Get OpenAI API key."""
    return os.getenv("OPENAI_API_KEY", "")


# ============================================
# CLI Entry Point
# ============================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate environment configuration")
    parser.add_argument("--strict", action="store_true", help="Exit on validation failure")
    parser.add_argument("--show-config", action="store_true", help="Display configuration")
    args = parser.parse_args()

    result = validate_environment(strict=args.strict, log_config=args.show_config)

    if result.valid:
        print("✅ Environment validation passed!")
    else:
        print("❌ Environment validation failed!")
        sys.exit(1)

    if result.warnings:
        print("\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
