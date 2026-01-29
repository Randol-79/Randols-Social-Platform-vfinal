"""
Database Connection and Repository Layer
MongoDB integration with async support
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, TypeVar

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from utils.config import Config
from utils.logger import setup_logger

from .models import (
    ABTest,
    AgentLog,
    AgentState,
    AuditLog,
    ContentCalendar,
    ContentInDB,
    ContentStatus,
    ContentType,
    DailyAnalytics,
    EmergencyOverride,
    Notification,
    Platform,
    ScheduledPost,
    SystemConfig,
    WeeklyReport,
    deserialize_doc,
    serialize_doc,
)

logger = setup_logger("database")


class DatabaseManager:
    """
    MongoDB Database Manager with connection pooling and health checks
    """

    _instance = None
    _async_client: Optional[AsyncIOMotorClient] = None
    _sync_client: Optional[MongoClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.mongodb_uri = Config.MONGODB_URI
            self.database_name = self._extract_db_name()
            self._initialized = True
            logger.info(f"DatabaseManager initialized for database: {self.database_name}")

    def _extract_db_name(self) -> str:
        """Extract database name from URI"""
        if "/" in self.mongodb_uri:
            db_part = self.mongodb_uri.split("/")[-1]
            return db_part.split("?")[0] or "randols_marketing"
        return "randols_marketing"

    # ========================
    # Connection Management
    # ========================

    def get_sync_client(self) -> MongoClient:
        """Get synchronous MongoDB client"""
        if self._sync_client is None:
            self._sync_client = MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10,
            )
        return self._sync_client

    def get_async_client(self) -> AsyncIOMotorClient:
        """Get asynchronous MongoDB client (Motor)"""
        if self._async_client is None:
            self._async_client = AsyncIOMotorClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10,
            )
        return self._async_client

    def get_sync_db(self) -> Any:
        """Get synchronous database instance"""
        return self.get_sync_client()[self.database_name]

    def get_async_db(self) -> AsyncIOMotorDatabase:
        """Get asynchronous database instance"""
        return self.get_async_client()[self.database_name]

    # ========================
    # Health Checks
    # ========================

    def check_health(self) -> Dict[str, Any]:
        """Check database health synchronously"""
        try:
            client = self.get_sync_client()
            client.admin.command("ping")
            return {
                "status": "healthy",
                "connected": True,
                "database": self.database_name,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def check_health_async(self) -> Dict[str, Any]:
        """Check database health asynchronously"""
        try:
            client = self.get_async_client()
            await client.admin.command("ping")
            return {
                "status": "healthy",
                "connected": True,
                "database": self.database_name,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Async database health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    # ========================
    # Index Management
    # ========================

    async def create_indexes(self):
        """Create database indexes for optimal performance"""
        db = self.get_async_db()

        # Content indexes
        await db.content.create_index([("status", ASCENDING)])
        await db.content.create_index([("content_type", ASCENDING)])
        await db.content.create_index([("platforms", ASCENDING)])
        await db.content.create_index([("scheduled_for", ASCENDING)])
        await db.content.create_index([("created_at", DESCENDING)])
        await db.content.create_index([("status", ASCENDING), ("scheduled_for", ASCENDING)])

        # Schedule indexes
        await db.scheduled_posts.create_index([("scheduled_time", ASCENDING)])
        await db.scheduled_posts.create_index([("platform", ASCENDING)])
        await db.scheduled_posts.create_index([("status", ASCENDING)])
        await db.scheduled_posts.create_index(
            [("status", ASCENDING), ("scheduled_time", ASCENDING)]
        )

        # Analytics indexes
        await db.daily_analytics.create_index([("date", DESCENDING)], unique=True)
        await db.weekly_reports.create_index([("week_start", DESCENDING)])

        # Agent logs index with TTL (auto-delete after 30 days)
        await db.agent_logs.create_index([("timestamp", DESCENDING)])
        await db.agent_logs.create_index(
            [("timestamp", ASCENDING)], expireAfterSeconds=30 * 24 * 60 * 60  # 30 days
        )

        # Audit log indexes
        await db.audit_logs.create_index([("timestamp", DESCENDING)])
        await db.audit_logs.create_index([("entity_type", ASCENDING), ("entity_id", ASCENDING)])

        # Notifications index
        await db.notifications.create_index([("sent_at", DESCENDING)])
        await db.notifications.create_index([("read", ASCENDING)])

        logger.info("Database indexes created successfully")

    # ========================
    # Cleanup
    # ========================

    def close_connections(self):
        """Close all database connections"""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        if self._async_client:
            self._async_client.close()
            self._async_client = None
        logger.info("Database connections closed")


# ========================
# Repository Classes
# ========================


class ContentRepository:
    """Repository for content operations"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        self.collection_name = "content"

    @property
    def collection(self):
        return self.db_manager.get_async_db()[self.collection_name]

    async def create(self, content: Dict[str, Any]) -> str:
        """Create new content"""
        content["created_at"] = datetime.utcnow()
        content["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(content)

        # Log the action
        await self._log_action("create", str(result.inserted_id), content)

        return str(result.inserted_id)

    async def get_by_id(self, content_id: str) -> Optional[Dict]:
        """Get content by ID"""
        from bson import ObjectId

        try:
            doc = await self.collection.find_one({"_id": ObjectId(content_id)})
            return serialize_doc(doc) if doc else None
        except Exception as e:
            logger.error(f"Error fetching content {content_id}: {e}")
            return None

    async def update(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """Update content"""
        from bson import ObjectId

        updates["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one({"_id": ObjectId(content_id)}, {"$set": updates})

        if result.modified_count > 0:
            await self._log_action("update", content_id, updates)

        return result.modified_count > 0

    async def delete(self, content_id: str) -> bool:
        """Delete content (soft delete by changing status)"""
        return await self.update(content_id, {"status": ContentStatus.ARCHIVED.value})

    async def get_by_status(self, status: ContentStatus, limit: int = 100) -> List[Dict]:
        """Get content by status"""
        cursor = (
            self.collection.find({"status": status.value})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )

        return [serialize_doc(doc) async for doc in cursor]

    async def get_scheduled(self, start: datetime = None, end: datetime = None) -> List[Dict]:
        """Get scheduled content within date range"""
        query = {"status": ContentStatus.SCHEDULED.value}

        if start:
            query["scheduled_for"] = {"$gte": start}
        if end:
            query.setdefault("scheduled_for", {})["$lte"] = end

        cursor = self.collection.find(query).sort("scheduled_for", ASCENDING)
        return [serialize_doc(doc) async for doc in cursor]

    async def get_for_platform(
        self, platform: Platform, status: ContentStatus = None, limit: int = 50
    ) -> List[Dict]:
        """Get content for specific platform"""
        query = {"platforms": platform.value}
        if status:
            query["status"] = status.value

        cursor = self.collection.find(query).sort("created_at", DESCENDING).limit(limit)
        return [serialize_doc(doc) async for doc in cursor]

    async def get_by_type(self, content_type: ContentType, limit: int = 50) -> List[Dict]:
        """Get content by type"""
        cursor = (
            self.collection.find({"content_type": content_type.value})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )

        return [serialize_doc(doc) async for doc in cursor]

    async def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search on content"""
        cursor = self.collection.find({"$text": {"$search": query}}).limit(limit)

        return [serialize_doc(doc) async for doc in cursor]

    async def get_recent(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Get recent content"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        cursor = (
            self.collection.find({"created_at": {"$gte": cutoff}})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )

        return [serialize_doc(doc) async for doc in cursor]

    async def update_metrics(self, content_id: str, platform: str, metrics: Dict) -> bool:
        """Update content metrics for a platform"""
        from bson import ObjectId

        result = await self.collection.update_one(
            {"_id": ObjectId(content_id)},
            {"$set": {f"metrics.{platform}": metrics, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count > 0

    async def _log_action(self, action: str, entity_id: str, data: Dict):
        """Log content action"""
        log_collection = self.db_manager.get_async_db()["audit_logs"]
        await log_collection.insert_one(
            {
                "action": action,
                "entity_type": "content",
                "entity_id": entity_id,
                "changes": data,
                "timestamp": datetime.utcnow(),
            }
        )


class ScheduleRepository:
    """Repository for schedule operations"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        self.collection_name = "scheduled_posts"

    @property
    def collection(self):
        return self.db_manager.get_async_db()[self.collection_name]

    async def create(self, post: Dict[str, Any]) -> str:
        """Create scheduled post"""
        post["created_at"] = datetime.utcnow()
        result = await self.collection.insert_one(post)
        return str(result.inserted_id)

    async def get_pending(self, before: datetime = None) -> List[Dict]:
        """Get pending posts due for publishing"""
        query = {"status": "pending"}
        if before:
            query["scheduled_time"] = {"$lte": before}
        else:
            query["scheduled_time"] = {"$lte": datetime.utcnow()}

        cursor = self.collection.find(query).sort("scheduled_time", ASCENDING)
        return [serialize_doc(doc) async for doc in cursor]

    async def get_for_date(self, date: str) -> List[Dict]:
        """Get scheduled posts for a date (YYYY-MM-DD)"""
        start = datetime.strptime(date, "%Y-%m-%d")
        end = start + timedelta(days=1)

        cursor = self.collection.find({"scheduled_time": {"$gte": start, "$lt": end}}).sort(
            "scheduled_time", ASCENDING
        )

        return [serialize_doc(doc) async for doc in cursor]

    async def update_status(self, post_id: str, status: str, **kwargs) -> bool:
        """Update post status"""
        from bson import ObjectId

        updates = {"status": status, **kwargs}
        result = await self.collection.update_one({"_id": ObjectId(post_id)}, {"$set": updates})
        return result.modified_count > 0

    async def mark_published(self, post_id: str, platform_post_id: str) -> bool:
        """Mark post as published"""
        return await self.update_status(
            post_id, "published", post_id=platform_post_id, published_at=datetime.utcnow()
        )

    async def mark_failed(self, post_id: str, error: str) -> bool:
        """Mark post as failed"""
        from bson import ObjectId

        result = await self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"status": "failed", "error_message": error}, "$inc": {"retry_count": 1}},
        )
        return result.modified_count > 0

    async def get_failed_for_retry(self, max_retries: int = 3) -> List[Dict]:
        """Get failed posts eligible for retry"""
        cursor = self.collection.find({"status": "failed", "retry_count": {"$lt": max_retries}})
        return [serialize_doc(doc) async for doc in cursor]

    async def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        return await self.update_status(post_id, "cancelled")

    async def bulk_pause(self, content_ids: List[str]) -> int:
        """Pause multiple scheduled posts"""
        result = await self.collection.update_many(
            {"content_id": {"$in": content_ids}, "status": "pending"},
            {"$set": {"status": "paused"}},
        )
        return result.modified_count

    async def bulk_resume(self, content_ids: List[str] = None) -> int:
        """Resume paused posts"""
        query = {"status": "paused"}
        if content_ids:
            query["content_id"] = {"$in": content_ids}

        result = await self.collection.update_many(query, {"$set": {"status": "pending"}})
        return result.modified_count


class AnalyticsRepository:
    """Repository for analytics operations"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    @property
    def daily_collection(self):
        return self.db_manager.get_async_db()["daily_analytics"]

    @property
    def weekly_collection(self):
        return self.db_manager.get_async_db()["weekly_reports"]

    async def save_daily(self, date: str, analytics: Dict[str, Any]) -> str:
        """Save or update daily analytics"""
        result = await self.daily_collection.update_one(
            {"date": date},
            {"$set": {**analytics, "date": date, "updated_at": datetime.utcnow()}},
            upsert=True,
        )
        return date

    async def get_daily(self, date: str) -> Optional[Dict]:
        """Get daily analytics"""
        doc = await self.daily_collection.find_one({"date": date})
        return serialize_doc(doc) if doc else None

    async def get_daily_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get daily analytics for date range"""
        cursor = self.daily_collection.find({"date": {"$gte": start_date, "$lte": end_date}}).sort(
            "date", DESCENDING
        )

        return [serialize_doc(doc) async for doc in cursor]

    async def save_weekly(self, report: Dict[str, Any]) -> str:
        """Save weekly report"""
        result = await self.weekly_collection.insert_one(
            {**report, "generated_at": datetime.utcnow()}
        )
        return str(result.inserted_id)

    async def get_weekly_reports(self, limit: int = 12) -> List[Dict]:
        """Get recent weekly reports"""
        cursor = self.weekly_collection.find().sort("week_start", DESCENDING).limit(limit)

        return [serialize_doc(doc) async for doc in cursor]

    async def get_platform_summary(self, platform: str, days: int = 30) -> Dict[str, Any]:
        """Get platform analytics summary"""
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

        pipeline = [
            {"$match": {"date": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": None,
                    "total_posts": {"$sum": f"$platforms.{platform}.total_posts"},
                    "total_impressions": {"$sum": f"$platforms.{platform}.total_impressions"},
                    "total_engagement": {"$sum": f"$platforms.{platform}.total_engagement"},
                    "avg_engagement_rate": {"$avg": f"$platforms.{platform}.avg_engagement_rate"},
                }
            },
        ]

        async for result in self.daily_collection.aggregate(pipeline):
            return result

        return {}


class AgentRepository:
    """Repository for agent state and logs"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    @property
    def state_collection(self):
        return self.db_manager.get_async_db()["agent_states"]

    @property
    def log_collection(self):
        return self.db_manager.get_async_db()["agent_logs"]

    async def update_state(self, agent_name: str, state: Dict[str, Any]) -> bool:
        """Update agent state"""
        result = await self.state_collection.update_one(
            {"agent_name": agent_name},
            {"$set": {**state, "agent_name": agent_name, "updated_at": datetime.utcnow()}},
            upsert=True,
        )
        return result.upserted_id is not None or result.modified_count > 0

    async def get_state(self, agent_name: str) -> Optional[Dict]:
        """Get agent state"""
        doc = await self.state_collection.find_one({"agent_name": agent_name})
        return serialize_doc(doc) if doc else None

    async def get_all_states(self) -> List[Dict]:
        """Get all agent states"""
        cursor = self.state_collection.find()
        return [serialize_doc(doc) async for doc in cursor]

    async def log_action(self, agent_name: str, action: str, status: str, details: Dict = None):
        """Log agent action"""
        await self.log_collection.insert_one(
            {
                "agent_name": agent_name,
                "action": action,
                "status": status,
                "details": details or {},
                "timestamp": datetime.utcnow(),
            }
        )

    async def get_logs(self, agent_name: str = None, limit: int = 100) -> List[Dict]:
        """Get agent logs"""
        query = {}
        if agent_name:
            query["agent_name"] = agent_name

        cursor = self.log_collection.find(query).sort("timestamp", DESCENDING).limit(limit)

        return [serialize_doc(doc) async for doc in cursor]

    async def get_error_logs(self, hours: int = 24) -> List[Dict]:
        """Get recent error logs"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor = self.log_collection.find({"status": "error", "timestamp": {"$gte": cutoff}}).sort(
            "timestamp", DESCENDING
        )

        return [serialize_doc(doc) async for doc in cursor]


class NotificationRepository:
    """Repository for notifications"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        self.collection_name = "notifications"

    @property
    def collection(self):
        return self.db_manager.get_async_db()[self.collection_name]

    async def create(self, notification: Dict[str, Any]) -> str:
        """Create notification"""
        notification["sent_at"] = datetime.utcnow()
        notification["read"] = False
        result = await self.collection.insert_one(notification)
        return str(result.inserted_id)

    async def get_unread(self, limit: int = 50) -> List[Dict]:
        """Get unread notifications"""
        cursor = self.collection.find({"read": False}).sort("sent_at", DESCENDING).limit(limit)

        return [serialize_doc(doc) async for doc in cursor]

    async def mark_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        from bson import ObjectId

        result = await self.collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"read": True, "read_at": datetime.utcnow()}},
        )
        return result.modified_count > 0

    async def mark_all_read(self) -> int:
        """Mark all notifications as read"""
        result = await self.collection.update_many(
            {"read": False}, {"$set": {"read": True, "read_at": datetime.utcnow()}}
        )
        return result.modified_count


# ========================
# Database Initialization
# ========================


async def initialize_database():
    """Initialize database with indexes and default data"""
    db_manager = DatabaseManager()

    # Check connection
    health = await db_manager.check_health_async()
    if health["status"] != "healthy":
        raise Exception(f"Database not healthy: {health.get('error')}")

    # Create indexes
    await db_manager.create_indexes()

    # Create text index for content search
    db = db_manager.get_async_db()
    await db.content.create_index([("text", "text")])

    logger.info("Database initialization complete")
    return True


# Singleton instance
db_manager = DatabaseManager()
