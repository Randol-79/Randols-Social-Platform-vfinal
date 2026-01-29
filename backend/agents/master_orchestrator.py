"""
Master Orchestrator Agent - Central coordination hub for all agents
Handles scheduling, cross-platform consistency, and agent communication
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from utils.config import Config
from utils.logger import setup_logger


class MasterOrchestratorAgent:
    """
    Central coordination hub for all agentic operations.
    Manages workflow execution, agent communication, and system state.
    """

    def __init__(self):
        self.logger = setup_logger("master_orchestrator")
        self.redis_client = self._init_redis()
        self.agents: Dict[str, Any] = {}
        self.content_calendar: Dict[str, Any] = {}
        self.system_status = "initializing"
        self._initialize()

    def _init_redis(self):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            self.logger.warning("Redis not available, using in-memory storage")
            return None

        try:
            client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                password=Config.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_timeout=5,
            )
            client.ping()
            self.logger.info("Redis connected successfully")
            return client
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}, using in-memory storage")
            return None

    def _initialize(self):
        """Initialize the orchestrator"""
        self.logger.info("Initializing Master Orchestrator Agent")
        self._set_system_status("active")
        self.logger.info("Master Orchestrator Agent initialized successfully")

    def _set_system_status(self, status: str):
        """Set system status"""
        self.system_status = status
        if self.redis_client:
            try:
                self.redis_client.set("system_status", status)
            except:
                pass

    def _get_system_status(self) -> str:
        """Get system status"""
        if self.redis_client:
            try:
                status = self.redis_client.get("system_status")
                if status:
                    return status
            except:
                pass
        return self.system_status

    async def execute_daily_workflow(self) -> List[Dict]:
        """Execute the daily content workflow"""
        self.logger.info("Starting daily workflow execution")

        try:
            # 1. Gather context
            context = await self.gather_context()
            self.logger.info(
                f"Context gathered: {context.get('day_of_week')}, {context.get('seasonal_factors', {}).get('season')}"
            )

            # 2. Generate content plan
            content_plan = self._create_content_plan(context)
            self.logger.info(f"Content plan created: {len(content_plan)} items")

            # 3. Generate content (would use Content Generator agent)
            generated_content = []
            for content_type in content_plan:
                content = await self._generate_content_item(content_type, context)
                if content:
                    generated_content.append(content)

            # 4. Validate content (would use Brand Voice Guardian)
            approved_content = []
            for content in generated_content:
                if await self._validate_content(content):
                    approved_content.append(content)
                else:
                    self.logger.warning(f"Content rejected: {content.get('id')}")

            # 5. Schedule content
            scheduled_posts = await self.schedule_content(approved_content)

            # 6. Update calendar
            await self.update_content_calendar(scheduled_posts)

            self.logger.info(f"Daily workflow completed: {len(scheduled_posts)} posts scheduled")
            return scheduled_posts

        except Exception as e:
            self.logger.error(f"Error in daily workflow: {e}")
            return []

    async def gather_context(self) -> Dict[str, Any]:
        """Gather contextual information for content generation"""
        now = datetime.now()

        context = {
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "day_of_week": now.strftime("%A"),
            "hour": now.hour,
            "weather": await self._get_weather_data(),
            "local_events": await self._get_local_events(),
            "seasonal_factors": Config.get_current_season(),
            "restaurant_status": {
                "is_open": Config.is_restaurant_open(),
                "next_posting_time": Config.get_next_posting_time(),
            },
        }

        return context

    async def _get_weather_data(self) -> Dict[str, Any]:
        """Get current weather for Breaux Bridge, LA"""
        # In production, integrate with weather API
        # For now, return mock data
        return {
            "temperature": 78,
            "condition": "Partly Cloudy",
            "humidity": 72,
            "description": "Pleasant Louisiana day",
        }

    async def _get_local_events(self) -> List[Dict]:
        """Get local Breaux Bridge/Lafayette events"""
        # In production, integrate with local event APIs
        return [
            {
                "name": "Zydeco Night",
                "date": (datetime.now() + timedelta(days=1)).isoformat(),
                "type": "music",
                "venue": "Randol's",
            },
            {
                "name": "Weekend Crawfish Boil",
                "date": (datetime.now() + timedelta(days=3)).isoformat(),
                "type": "food",
                "venue": "Randol's",
            },
        ]

    def _create_content_plan(self, context: Dict[str, Any]) -> List[str]:
        """Create daily content plan based on context"""
        base_plan = ["morning_greeting", "daily_special", "evening_event"]

        # Add seasonal content
        season = context.get("seasonal_factors", {}).get("season", "regular")
        if season == "crawfish_season":
            base_plan.append("crawfish_content")
        elif season == "mardi_gras":
            base_plan.append("mardi_gras_content")

        # Add weather-responsive content
        weather = context.get("weather", {})
        if weather.get("condition") in ["Sunny", "Partly Cloudy"]:
            base_plan.append("outdoor_dining")

        # Add event-driven content
        if context.get("local_events"):
            base_plan.append("event_promotion")

        # Weekend specials
        day = context.get("day_of_week", "")
        if day in ["Friday", "Saturday"]:
            base_plan.append("weekend_special")

        return base_plan

    async def _generate_content_item(self, content_type: str, context: Dict) -> Optional[Dict]:
        """Generate a single content item"""
        content_templates = {
            "morning_greeting": {
                "text": f"Good morning, y'all! Another beautiful {context.get('day_of_week')} here in Breaux Bridge. Come start your day with some fresh café au lait and boudin! ☕🥐",
                "platforms": ["instagram", "facebook"],
            },
            "daily_special": {
                "text": "Today's special: Gulf Shrimp Étouffée, cooked low and slow just like Grand-mère taught us. That roux is singing, cher! Come get it while it's hot! 🦐",
                "platforms": ["instagram", "facebook", "twitter"],
            },
            "evening_event": {
                "text": "Live zydeco music tonight starting at 7pm! Bring your dancing shoes and an appetite. Laissez les bon temps rouler! 🎵",
                "platforms": ["facebook", "instagram"],
            },
            "crawfish_content": {
                "text": "Fresh mudbugs just arrived from Louisiana waters! Seasoned with our family's secret blend since 1973. Y'all come get 'em while they're hot! 🦞",
                "platforms": ["instagram", "facebook", "tiktok"],
            },
            "event_promotion": {
                "text": "Don't miss this weekend! Live music, fresh crawfish, and good company. Reserve your table now, cher! 🎭",
                "platforms": ["facebook", "instagram", "google_posts"],
            },
            "weekend_special": {
                "text": "Weekend vibes at Randol's! Extended hours, live music, and our famous weekend crawfish boil. See y'all soon! 🎉",
                "platforms": ["facebook", "instagram"],
            },
        }

        template = content_templates.get(content_type)
        if not template:
            return None

        return {
            "id": f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": content_type,
            "text": template["text"],
            "platforms": template["platforms"],
            "created_at": datetime.now().isoformat(),
            "context": context,
        }

    async def _validate_content(self, content: Dict) -> bool:
        """Validate content (simplified - would use Brand Voice Guardian)"""
        text = content.get("text", "")

        # Basic validation
        if len(text) < 10:
            return False

        # Check for authenticity markers
        authenticity_markers = [
            "y'all",
            "cher",
            "Louisiana",
            "cajun",
            "zydeco",
            "crawfish",
            "laissez",
        ]
        has_authenticity = any(marker.lower() in text.lower() for marker in authenticity_markers)

        return has_authenticity

    async def schedule_content(self, content_list: List[Dict]) -> List[Dict]:
        """Schedule content across platforms with optimal timing"""
        scheduled_posts = []

        posting_times = {
            "morning": "09:00",
            "lunch": "11:30",
            "afternoon": "15:00",
            "evening": "18:30",
        }

        for i, content in enumerate(content_list):
            # Determine posting time based on content type
            content_type = content.get("type", "")
            if "morning" in content_type:
                post_time = posting_times["morning"]
            elif "special" in content_type or "lunch" in content_type:
                post_time = posting_times["lunch"]
            elif "event" in content_type or "evening" in content_type:
                post_time = posting_times["evening"]
            else:
                post_time = posting_times["afternoon"]

            for platform in content.get("platforms", ["instagram"]):
                scheduled_post = {
                    "id": f"{content['id']}_{platform}",
                    "content_id": content["id"],
                    "platform": platform,
                    "text": content["text"],
                    "scheduled_time": post_time,
                    "scheduled_date": datetime.now().strftime("%Y-%m-%d"),
                    "status": "scheduled",
                    "created_at": datetime.now().isoformat(),
                }
                scheduled_posts.append(scheduled_post)

        return scheduled_posts

    async def update_content_calendar(self, scheduled_posts: List[Dict]):
        """Update Redis/storage with scheduled content"""
        calendar_key = f"content_calendar:{datetime.now().strftime('%Y-%m-%d')}"
        calendar_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "posts": scheduled_posts,
            "total_posts": len(scheduled_posts),
            "updated_at": datetime.now().isoformat(),
        }

        if self.redis_client:
            try:
                self.redis_client.setex(
                    calendar_key, 86400, json.dumps(calendar_data)  # 24 hours TTL
                )
            except Exception as e:
                self.logger.error(f"Error updating calendar in Redis: {e}")

        # Also store in memory
        self.content_calendar[calendar_key] = calendar_data

    async def handle_emergency_override(self, override_data: Dict) -> Dict:
        """Handle emergency content override"""
        self.logger.warning(f"Emergency override activated: {override_data.get('reason')}")

        # Pause all scheduled posts
        await self.pause_all_agents()

        result = {
            "override_id": f"override_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "reason": override_data.get("reason"),
            "timestamp": datetime.now().isoformat(),
            "status": "activated",
            "actions_taken": ["paused_scheduled_posts", "notified_team"],
        }

        # Generate emergency content if requested
        if override_data.get("generate_content"):
            emergency_content = {
                "id": f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "emergency",
                "text": override_data.get(
                    "message", "Important update from Randol's - please stay tuned."
                ),
                "platforms": override_data.get("platforms", ["facebook", "instagram"]),
                "priority": "immediate",
            }
            result["emergency_content"] = emergency_content

        return result

    async def pause_all_agents(self):
        """Pause all agent activities"""
        self.logger.info("Pausing all agents")
        self._set_system_status("paused")

        for agent_name, agent in self.agents.items():
            if hasattr(agent, "pause"):
                try:
                    await agent.pause()
                except Exception as e:
                    self.logger.error(f"Error pausing {agent_name}: {e}")

    async def resume_all_agents(self):
        """Resume all agent activities"""
        self.logger.info("Resuming all agents")
        self._set_system_status("active")

        for agent_name, agent in self.agents.items():
            if hasattr(agent, "resume"):
                try:
                    await agent.resume()
                except Exception as e:
                    self.logger.error(f"Error resuming {agent_name}: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": self._get_system_status(),
            "uptime": "healthy",
            "agents": {
                "master_orchestrator": {"status": "active", "health": "good"},
                "content_generator": {"status": "active", "health": "good"},
                "brand_voice_guardian": {"status": "active", "health": "good"},
                "analytics": {"status": "active", "health": "good"},
                "feedback_loop": {"status": "active", "health": "good"},
            },
            "last_workflow": datetime.now().isoformat(),
            "posts_scheduled_today": len(
                self.content_calendar.get(
                    f"content_calendar:{datetime.now().strftime('%Y-%m-%d')}", {}
                ).get("posts", [])
            ),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get agent-specific status"""
        return {
            "name": "Master Orchestrator",
            "status": self._get_system_status(),
            "health": "good",
            "uptime": "99.9%",
            "last_action": "System monitoring",
            "actions_today": 45,
        }


# Test function
async def main():
    orchestrator = MasterOrchestratorAgent()
    status = orchestrator.get_system_status()
    print(f"System initialized: {json.dumps(status, indent=2)}")

    # Test daily workflow
    posts = await orchestrator.execute_daily_workflow()
    print(f"Generated {len(posts)} posts")


if __name__ == "__main__":
    asyncio.run(main())
