"""
Daily Content Generation Job
Runs every morning to generate the day's social media content
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.brand_voice_guardian import BrandVoiceGuardianAgent
from agents.content_generator import ContentGeneratorAgent
from agents.master_orchestrator import MasterOrchestratorAgent
from agents.scheduler_agent import SchedulerAgent
from utils.config import Config
from utils.logger import setup_logger


class DailyContentJob:
    """Daily content generation job"""

    def __init__(self):
        self.logger = setup_logger("daily_content_job")
        self.orchestrator = None
        self.content_generator = None
        self.brand_guardian = None
        self.scheduler = None

    def _initialize_agents(self):
        """Lazy initialization of agents"""
        if self.orchestrator is None:
            self.orchestrator = MasterOrchestratorAgent()
        if self.content_generator is None:
            self.content_generator = ContentGeneratorAgent()
        if self.brand_guardian is None:
            self.brand_guardian = BrandVoiceGuardianAgent()
        if self.scheduler is None:
            self.scheduler = SchedulerAgent()

    async def run(self):
        """Execute daily content generation"""
        start_time = datetime.now()
        self.logger.info("=" * 50)
        self.logger.info("Daily Content Generation Job Starting")
        self.logger.info(f"Start time: {start_time.isoformat()}")
        self.logger.info("=" * 50)

        try:
            self._initialize_agents()

            # Step 1: Gather context
            self.logger.info("Step 1: Gathering context...")
            context = await self._gather_context()

            # Step 2: Generate content plan
            self.logger.info("Step 2: Creating content plan...")
            content_plan = self._create_content_plan(context)
            self.logger.info(f"Planned {len(content_plan)} content pieces")

            # Step 3: Generate content
            self.logger.info("Step 3: Generating content...")
            generated_content = await self._generate_content(content_plan, context)
            self.logger.info(f"Generated {len(generated_content)} content pieces")

            # Step 4: Validate content
            self.logger.info("Step 4: Validating content...")
            validated_content = await self._validate_content(generated_content)
            approved = [c for c in validated_content if c.get("approved", False)]
            self.logger.info(f"Approved {len(approved)}/{len(validated_content)} content pieces")

            # Step 5: Schedule approved content
            self.logger.info("Step 5: Scheduling content...")
            scheduled = await self._schedule_content(approved)
            self.logger.info(f"Scheduled {len(scheduled)} posts")

            # Step 6: Generate report
            duration = (datetime.now() - start_time).total_seconds()
            report = self._generate_report(
                context, content_plan, generated_content, validated_content, scheduled, duration
            )

            self.logger.info("=" * 50)
            self.logger.info("Daily Content Generation Complete")
            self.logger.info(f"Duration: {duration:.2f} seconds")
            self.logger.info(f"Generated: {len(generated_content)}")
            self.logger.info(f"Approved: {len(approved)}")
            self.logger.info(f"Scheduled: {len(scheduled)}")
            self.logger.info("=" * 50)

            # Send notification
            await self._send_notification(report)

            return report

        except Exception as e:
            self.logger.error(f"Daily content job failed: {str(e)}")
            await self._send_error_notification(str(e))
            raise

    async def _gather_context(self) -> dict:
        """Gather context for content generation"""
        now = datetime.now()

        context = {
            "date": now.strftime("%Y-%m-%d"),
            "day_of_week": now.strftime("%A").lower(),
            "time": now.strftime("%H:%M"),
            "weather": await self._get_weather(),
            "local_events": await self._get_local_events(),
            "seasonal_factors": self._get_seasonal_factors(now),
            "restaurant_hours": self._get_restaurant_hours(now),
            "special_occasions": self._get_special_occasions(now),
        }

        return context

    async def _get_weather(self) -> dict:
        """Get current weather"""
        # Mock weather data - integrate with weather API in production
        return {
            "condition": "sunny",
            "temperature": 75,
            "humidity": 65,
            "description": "Clear skies",
        }

    async def _get_local_events(self) -> list:
        """Get local events"""
        # Mock events - integrate with events API in production
        return [
            {"name": "Zydeco Night", "date": datetime.now().strftime("%Y-%m-%d"), "time": "19:00"},
            {
                "name": "Crawfish Festival",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": "11:00",
            },
        ]

    def _get_seasonal_factors(self, now: datetime) -> dict:
        """Get seasonal factors"""
        month = now.month

        seasons = {
            (3, 4, 5): {"season": "crawfish_season", "theme": "Fresh Louisiana Crawfish"},
            (6, 7, 8): {"season": "summer", "theme": "Summer Festival Season"},
            (9, 10, 11): {"season": "fall", "theme": "Gumbo Weather"},
            (12, 1, 2): {"season": "winter", "theme": "Holiday Celebrations"},
        }

        for months, data in seasons.items():
            if month in months:
                return data

        return {"season": "general", "theme": "Authentic Cajun Cuisine"}

    def _get_restaurant_hours(self, now: datetime) -> dict:
        """Get restaurant hours for today"""
        day = now.strftime("%A").lower()
        schedule = Config.POSTING_SCHEDULE.get(day, {})

        return {
            "open": True,
            "morning_post": schedule.get("morning", "08:00"),
            "evening_post": schedule.get("evening", "17:00"),
        }

    def _get_special_occasions(self, now: datetime) -> list:
        """Check for special occasions"""
        occasions = []

        # Mardi Gras (simplified check)
        if now.month == 2 or (now.month == 3 and now.day < 5):
            occasions.append({"name": "Mardi Gras Season", "type": "festival"})

        # Crawfish season
        if now.month in [2, 3, 4, 5, 6]:
            occasions.append({"name": "Crawfish Season", "type": "seasonal"})

        return occasions

    def _create_content_plan(self, context: dict) -> list:
        """Create content plan for the day"""
        day = context["day_of_week"]

        # Base daily content
        plan = [
            {"type": "morning_greeting", "platforms": ["instagram", "facebook"], "time": "morning"},
            {
                "type": "daily_special",
                "platforms": ["instagram", "facebook", "google_posts"],
                "time": "lunch",
            },
        ]

        # Add evening content on weekends or event days
        if day in ["friday", "saturday"] or context.get("local_events"):
            plan.append(
                {
                    "type": "evening_event",
                    "platforms": ["instagram", "facebook", "tiktok"],
                    "time": "evening",
                }
            )

        # Add seasonal content
        season = context.get("seasonal_factors", {}).get("season", "")
        if "crawfish" in season:
            plan.append(
                {
                    "type": "crawfish_education",
                    "platforms": ["instagram", "tiktok"],
                    "time": "afternoon",
                }
            )

        return plan

    async def _generate_content(self, plan: list, context: dict) -> list:
        """Generate content based on plan"""
        generated = []

        for item in plan:
            try:
                content = await self.content_generator.generate_content_by_type(
                    item["type"], context
                )
                if content:
                    content["planned_platforms"] = item["platforms"]
                    content["planned_time"] = item["time"]
                    generated.append(content)
            except Exception as e:
                self.logger.error(f"Failed to generate {item['type']}: {str(e)}")

        return generated

    async def _validate_content(self, content_list: list) -> list:
        """Validate all generated content"""
        validated = []

        for content in content_list:
            try:
                is_approved = await self.brand_guardian.validate_content(content)
                content["approved"] = is_approved

                if not is_approved:
                    content["suggestions"] = self.brand_guardian.suggest_improvements(
                        content.get("text", "")
                    )

                validated.append(content)
            except Exception as e:
                self.logger.error(f"Validation error for {content.get('id')}: {str(e)}")
                content["approved"] = False
                content["error"] = str(e)
                validated.append(content)

        return validated

    async def _schedule_content(self, approved_content: list) -> list:
        """Schedule approved content"""
        scheduled = []

        for content in approved_content:
            try:
                result = await self.scheduler.schedule_content(content)
                if result.get("success"):
                    scheduled.append(
                        {
                            "content_id": content.get("id"),
                            "scheduled_time": result.get("scheduled_time"),
                            "platforms": result.get("platforms"),
                        }
                    )
            except Exception as e:
                self.logger.error(f"Scheduling error for {content.get('id')}: {str(e)}")

        return scheduled

    def _generate_report(
        self,
        context: dict,
        plan: list,
        generated: list,
        validated: list,
        scheduled: list,
        duration: float,
    ) -> dict:
        """Generate job completion report"""
        approved_count = len([v for v in validated if v.get("approved")])

        return {
            "job": "daily_content_generation",
            "date": context["date"],
            "status": "completed",
            "duration_seconds": duration,
            "metrics": {
                "planned": len(plan),
                "generated": len(generated),
                "approved": approved_count,
                "rejected": len(validated) - approved_count,
                "scheduled": len(scheduled),
            },
            "context": {
                "day": context["day_of_week"],
                "weather": context["weather"]["condition"],
                "season": context["seasonal_factors"]["season"],
                "events": len(context.get("local_events", [])),
            },
            "scheduled_posts": scheduled,
        }

    async def _send_notification(self, report: dict):
        """Send completion notification"""
        # Integrate with Slack/Discord webhook
        self.logger.info(f"Job report: {report}")

    async def _send_error_notification(self, error: str):
        """Send error notification"""
        self.logger.error(f"Error notification: {error}")


def main():
    """Main entry point"""
    job = DailyContentJob()

    try:
        result = asyncio.run(job.run())
        print(f"Job completed: {result['status']}")
    except Exception as e:
        print(f"Job failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
