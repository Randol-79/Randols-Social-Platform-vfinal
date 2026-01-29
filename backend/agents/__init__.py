"""
Agents package for Randol's Agentic Marketing Platform
Multi-agent orchestration system for autonomous social media marketing
"""

from .analytics_agent import AnalyticsAgent
from .brand_voice_guardian import BrandVoiceGuardianAgent
from .content_generator import ContentGeneratorAgent
from .feedback_loop_agent import FeedbackLoopAgent
from .master_orchestrator import MasterOrchestratorAgent
from .platform_agents import (
    FacebookAgent,
    GooglePostsAgent,
    InstagramAgent,
    PlatformAgentManager,
    TikTokAgent,
    YouTubeAgent,
)
from .scheduler_agent import ContentQueue, SchedulerAgent

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
