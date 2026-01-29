"""
API Package for Randol's Agentic Marketing Platform
Flask REST API with WebSocket support
"""

from .routes import (
    admin_bp,
    agents_bp,
    analytics_bp,
    api_bp,
    content_bp,
    register_blueprints,
    schedule_bp,
)

__all__ = [
    "api_bp",
    "content_bp",
    "schedule_bp",
    "analytics_bp",
    "agents_bp",
    "admin_bp",
    "register_blueprints",
]
