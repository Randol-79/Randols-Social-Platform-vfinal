"""
Database Models for Randol's Agentic Marketing Platform
MongoDB document schemas with Pydantic validation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator
from bson import ObjectId
import json


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic compatibility"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    GOOGLE_POSTS = "google_posts"
    TWITTER = "twitter"


class ContentType(str, Enum):
    MORNING_GREETING = "morning_greeting"
    DAILY_SPECIAL = "daily_special"
    EVENING_EVENT = "evening_event"
    CRAWFISH_CONTENT = "crawfish_content"
    EVENT_PROMOTION = "event_promotion"
    WEEKEND_SPECIAL = "weekend_special"
    EMERGENCY = "emergency"
    USER_GENERATED = "user_generated"
    SEASONAL = "seasonal"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    INITIALIZING = "initializing"
    MAINTENANCE = "maintenance"


# ========================
# Content Models
# ========================

class ContentMedia(BaseModel):
    """Media attachment for content"""
    type: str = Field(..., description="Media type: image, video, carousel")
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    dimensions: Optional[Dict[str, int]] = None
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None


class ContentMetrics(BaseModel):
    """Performance metrics for content"""
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    sentiment_score: Optional[float] = None
    
    def calculate_engagement_rate(self, reach: int) -> float:
        if reach == 0:
            return 0.0
        total_engagement = self.likes + self.comments + self.shares + self.saves
        return round(total_engagement / reach, 4)


class ContentValidation(BaseModel):
    """Validation results from Brand Voice Guardian"""
    authenticity_score: float = Field(ge=0.0, le=1.0)
    tone_compliance: bool = True
    cultural_appropriateness: bool = True
    brand_consistency: bool = True
    issues: List[str] = []
    suggestions: List[str] = []
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validated_by: str = "brand_voice_guardian"


class ContentBase(BaseModel):
    """Base content model"""
    text: str = Field(..., min_length=1, max_length=10000)
    content_type: ContentType
    platforms: List[Platform]
    hashtags: List[str] = []
    media: List[ContentMedia] = []
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        return [tag if tag.startswith('#') else f'#{tag}' for tag in v]


class ContentCreate(ContentBase):
    """Content creation request"""
    context: Optional[Dict[str, Any]] = {}
    schedule_time: Optional[datetime] = None
    priority: str = "normal"  # high, normal, low


class ContentInDB(ContentBase):
    """Content document in MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    status: ContentStatus = ContentStatus.DRAFT
    validation: Optional[ContentValidation] = None
    metrics: Dict[str, ContentMetrics] = {}  # Per-platform metrics
    context: Dict[str, Any] = {}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Tracking
    created_by: str = "content_generator"
    approved_by: Optional[str] = None
    version: int = 1
    parent_id: Optional[str] = None  # For A/B testing variants
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class ContentResponse(ContentBase):
    """Content API response"""
    id: str
    status: ContentStatus
    validation: Optional[ContentValidation] = None
    metrics: Dict[str, ContentMetrics] = {}
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None


# ========================
# Schedule Models
# ========================

class ScheduledPost(BaseModel):
    """Scheduled post document"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    content_id: str
    platform: Platform
    scheduled_time: datetime
    status: str = "pending"  # pending, processing, published, failed
    
    # Publishing details
    post_id: Optional[str] = None  # Platform's post ID after publishing
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    priority: str = "normal"
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class ContentCalendar(BaseModel):
    """Daily content calendar"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    date: str  # YYYY-MM-DD
    scheduled_posts: List[ScheduledPost] = []
    total_posts: int = 0
    platforms_summary: Dict[str, int] = {}  # Platform -> post count
    status: str = "active"  # active, paused, completed
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ========================
# Analytics Models
# ========================

class PlatformAnalytics(BaseModel):
    """Platform-level analytics"""
    platform: Platform
    period_start: datetime
    period_end: datetime
    
    # Aggregated metrics
    total_posts: int = 0
    total_impressions: int = 0
    total_reach: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0
    
    # Top performers
    top_posts: List[str] = []  # Content IDs
    best_posting_time: Optional[str] = None
    best_content_type: Optional[str] = None
    
    # Growth
    follower_count: int = 0
    follower_growth: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DailyAnalytics(BaseModel):
    """Daily analytics summary"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    date: str  # YYYY-MM-DD
    
    platforms: Dict[str, PlatformAnalytics] = {}
    
    # Aggregated totals
    total_posts: int = 0
    total_impressions: int = 0
    total_reach: int = 0
    total_engagement: int = 0
    overall_engagement_rate: float = 0.0
    
    # Performance grade
    performance_grade: str = "B"
    trend: str = "stable"  # improving, stable, declining
    
    # Content type breakdown
    content_type_performance: Dict[str, float] = {}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class WeeklyReport(BaseModel):
    """Weekly performance report"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    week_start: str  # YYYY-MM-DD
    week_end: str
    
    # Summary metrics
    total_posts: int = 0
    total_impressions: int = 0
    total_reach: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0
    
    # Week-over-week comparison
    posts_vs_last_week: float = 0.0
    engagement_vs_last_week: float = 0.0
    reach_vs_last_week: float = 0.0
    
    # Performance breakdown
    platform_performance: Dict[str, Dict] = {}
    content_type_performance: Dict[str, Dict] = {}
    best_performing_posts: List[Dict] = []
    
    # AI recommendations
    recommendations: List[Dict] = []
    
    # Report metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sent_to: List[str] = []
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ========================
# Agent Models
# ========================

class AgentLog(BaseModel):
    """Agent activity log entry"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    agent_name: str
    action: str
    status: str  # success, error, warning
    details: Dict[str, Any] = {}
    duration_ms: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class AgentState(BaseModel):
    """Agent state document"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    agent_name: str
    status: AgentStatus = AgentStatus.ACTIVE
    health: str = "good"  # good, degraded, unhealthy
    
    # Performance
    actions_today: int = 0
    errors_today: int = 0
    success_rate: float = 1.0
    avg_response_time_ms: float = 0.0
    
    # State data
    last_action: Optional[str] = None
    last_action_time: Optional[datetime] = None
    current_task: Optional[str] = None
    
    # Configuration
    config: Dict[str, Any] = {}
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ========================
# A/B Testing Models
# ========================

class ABTest(BaseModel):
    """A/B test document"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None
    
    # Test configuration
    test_type: str  # content_style, posting_time, hashtag_strategy
    variable: str
    hypothesis: Optional[str] = None
    
    # Variants
    control_content_ids: List[str] = []
    variant_content_ids: List[str] = []
    
    # Results
    control_metrics: Optional[ContentMetrics] = None
    variant_metrics: Optional[ContentMetrics] = None
    winner: Optional[str] = None  # control, variant, inconclusive
    statistical_significance: Optional[float] = None
    
    # Timeline
    status: str = "draft"  # draft, active, completed, cancelled
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_days: int = 7
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ========================
# System Models
# ========================

class SystemConfig(BaseModel):
    """System configuration document"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    key: str
    value: Any
    description: Optional[str] = None
    category: str = "general"
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str = "system"
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class AuditLog(BaseModel):
    """Audit log for system changes"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    action: str
    entity_type: str  # content, schedule, config, agent
    entity_id: str
    
    changes: Dict[str, Any] = {}
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    user: str = "system"
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class EmergencyOverride(BaseModel):
    """Emergency override record"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    reason: str
    message: Optional[str] = None
    platforms: List[Platform] = []
    
    # Actions taken
    paused_posts: List[str] = []
    emergency_content_id: Optional[str] = None
    notifications_sent: List[str] = []
    
    # Status
    status: str = "active"  # active, resolved
    activated_at: datetime = Field(default_factory=datetime.utcnow)
    activated_by: str
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ========================
# Notification Models
# ========================

class Notification(BaseModel):
    """System notification"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    type: str  # alert, info, warning, error, success
    title: str
    message: str
    
    # Targeting
    channels: List[str] = ["dashboard"]  # dashboard, slack, email, discord
    recipients: List[str] = []
    
    # Status
    read: bool = False
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    
    # Related entity
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ========================
# Helper Functions
# ========================

def serialize_doc(doc: dict) -> dict:
    """Serialize MongoDB document for JSON response"""
    if doc is None:
        return None
    
    result = {}
    for key, value in doc.items():
        if key == "_id":
            result["id"] = str(value)
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    return result


def deserialize_doc(data: dict) -> dict:
    """Deserialize JSON data for MongoDB insertion"""
    if data is None:
        return None
    
    result = {}
    for key, value in data.items():
        if key == "id":
            if value and ObjectId.is_valid(value):
                result["_id"] = ObjectId(value)
        elif isinstance(value, str) and len(value) == 24:
            try:
                result[key] = ObjectId(value)
            except:
                result[key] = value
        elif isinstance(value, dict):
            result[key] = deserialize_doc(value)
        elif isinstance(value, list):
            result[key] = [deserialize_doc(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    return result
