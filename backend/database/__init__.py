"""
Database Package for Randol's Agentic Marketing Platform
"""

from .models import (
    ContentStatus,
    Platform,
    ContentType,
    AgentStatus,
    ContentMedia,
    ContentMetrics,
    ContentValidation,
    ContentBase,
    ContentCreate,
    ContentInDB,
    ContentResponse,
    ScheduledPost,
    ContentCalendar,
    PlatformAnalytics,
    DailyAnalytics,
    WeeklyReport,
    AgentLog,
    AgentState,
    ABTest,
    AuditLog,
    EmergencyOverride,
    Notification,
    SystemConfig,
    serialize_doc,
    deserialize_doc,
)

from .repository import (
    DatabaseManager,
    db_manager,
    ContentRepository,
    ScheduleRepository,
    AnalyticsRepository,
    AgentRepository,
    NotificationRepository,
    initialize_database,
)

__all__ = [
    # Enums
    "ContentStatus",
    "Platform",
    "ContentType",
    "AgentStatus",
    # Models
    "ContentMedia",
    "ContentMetrics",
    "ContentValidation",
    "ContentBase",
    "ContentCreate",
    "ContentInDB",
    "ContentResponse",
    "ScheduledPost",
    "ContentCalendar",
    "PlatformAnalytics",
    "DailyAnalytics",
    "WeeklyReport",
    "AgentLog",
    "AgentState",
    "ABTest",
    "AuditLog",
    "EmergencyOverride",
    "Notification",
    "SystemConfig",
    # Utilities
    "serialize_doc",
    "deserialize_doc",
    # Database
    "DatabaseManager",
    "db_manager",
    "ContentRepository",
    "ScheduleRepository",
    "AnalyticsRepository",
    "AgentRepository",
    "NotificationRepository",
    "initialize_database",
]
