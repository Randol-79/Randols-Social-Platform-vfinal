"""
Agents package for Randol's Agentic Marketing Platform
Multi-agent orchestration system for autonomous social media marketing
"""

from .master_orchestrator import MasterOrchestratorAgent
from .content_generator import ContentGeneratorAgent
from .brand_voice_guardian import BrandVoiceGuardianAgent
from .analytics_agent import AnalyticsAgent
from .feedback_loop_agent import FeedbackLoopAgent
from .scheduler_agent import SchedulerAgent, ContentQueue
from .platform_agents import (
    PlatformAgentManager,
    InstagramAgent,
    FacebookAgent,
    TikTokAgent,
    YouTubeAgent,
    GooglePostsAgent,
)

__all__ = [
    # Core Orchestration
    "MasterOrchestratorAgent",
    # Content Pipeline
    "ContentGeneratorAgent",
    "BrandVoiceGuardianAgent",
    # Analytics & Optimization
    "AnalyticsAgent",
    "FeedbackLoopAgent",
    # Scheduling
    "SchedulerAgent",
    "ContentQueue",
    # Platform-Specific Agents
    "PlatformAgentManager",
    "InstagramAgent",
    "FacebookAgent",
    "TikTokAgent",
    "YouTubeAgent",
    "GooglePostsAgent",
]
