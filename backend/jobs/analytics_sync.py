"""
Analytics Sync Job
Runs every 4 hours to collect and aggregate analytics from all platforms
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.logger import setup_logger
from agents.analytics_agent import AnalyticsAgent
from agents.platform_agents import PlatformAgentManager


class AnalyticsSyncJob:
    """Analytics synchronization job"""

    def __init__(self):
        self.logger = setup_logger("analytics_sync_job")
        self.analytics_agent = None
        self.platform_manager = None

    def _initialize(self):
        """Initialize agents"""
        if self.analytics_agent is None:
            self.analytics_agent = AnalyticsAgent()
        if self.platform_manager is None:
            self.platform_manager = PlatformAgentManager()

    async def run(self):
        """Execute analytics sync"""
        start_time = datetime.now()
        self.logger.info("=" * 50)
        self.logger.info("Analytics Sync Job Starting")
        self.logger.info(f"Start time: {start_time.isoformat()}")
        self.logger.info("=" * 50)

        try:
            self._initialize()

            # Step 1: Get recent posts to sync
            posts_to_sync = await self._get_posts_to_sync()
            self.logger.info(f"Found {len(posts_to_sync)} posts to sync")

            # Step 2: Fetch analytics for each platform
            platform_analytics = {}
            for platform in ["instagram", "facebook", "tiktok", "youtube", "google_posts"]:
                try:
                    analytics = await self._fetch_platform_analytics(platform, posts_to_sync)
                    platform_analytics[platform] = analytics
                    self.logger.info(f"Synced {len(analytics)} posts from {platform}")
                except Exception as e:
                    self.logger.error(f"Failed to sync {platform}: {str(e)}")

            # Step 3: Aggregate and store analytics
            aggregated = await self._aggregate_analytics(platform_analytics)

            # Step 4: Update performance metrics
            await self._update_performance_metrics(aggregated)

            # Step 5: Identify trends
            trends = await self._identify_trends(aggregated)

            # Generate report
            duration = (datetime.now() - start_time).total_seconds()
            report = {
                "job": "analytics_sync",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "posts_synced": sum(len(a) for a in platform_analytics.values()),
                "platforms_synced": list(platform_analytics.keys()),
                "trends_identified": len(trends),
                "summary": aggregated.get("summary", {}),
            }

            self.logger.info("=" * 50)
            self.logger.info("Analytics Sync Complete")
            self.logger.info(f"Duration: {duration:.2f}s")
            self.logger.info(f"Posts synced: {report['posts_synced']}")
            self.logger.info("=" * 50)

            return report

        except Exception as e:
            self.logger.error(f"Analytics sync failed: {str(e)}")
            raise

    async def _get_posts_to_sync(self) -> List[Dict]:
        """Get list of posts that need analytics synced"""
        # Get posts from last 7 days that need updated analytics
        # In production, query from database

        # Mock data
        posts = []
        for i in range(10):
            for platform in ["instagram", "facebook"]:
                posts.append(
                    {
                        "id": f"post_{i}_{platform}",
                        "platform": platform,
                        "posted_at": (datetime.now() - timedelta(days=i)).isoformat(),
                        "last_synced": (datetime.now() - timedelta(hours=6)).isoformat(),
                    }
                )

        return posts

    async def _fetch_platform_analytics(self, platform: str, posts: List[Dict]) -> List[Dict]:
        """Fetch analytics for a specific platform"""
        agent = self.platform_manager.get_agent(platform)
        if not agent:
            return []

        analytics = []
        platform_posts = [p for p in posts if p.get("platform") == platform]

        for post in platform_posts:
            try:
                data = await agent.get_analytics(post["id"])
                data["synced_at"] = datetime.now().isoformat()
                analytics.append(data)
            except Exception as e:
                self.logger.warning(f"Failed to get analytics for {post['id']}: {str(e)}")

        return analytics

    async def _aggregate_analytics(self, platform_analytics: Dict[str, List]) -> Dict:
        """Aggregate analytics across platforms"""
        total_impressions = 0
        total_engagement = 0
        total_reach = 0
        platform_summaries = {}

        for platform, analytics in platform_analytics.items():
            platform_total = {
                "impressions": 0,
                "engagement": 0,
                "reach": 0,
                "posts": len(analytics),
            }

            for post in analytics:
                platform_total["impressions"] += post.get("impressions", post.get("views", 0))
                platform_total["engagement"] += post.get("engagement", 0)
                platform_total["reach"] += post.get("reach", 0)

            total_impressions += platform_total["impressions"]
            total_engagement += platform_total["engagement"]
            total_reach += platform_total["reach"]
            platform_summaries[platform] = platform_total

        return {
            "summary": {
                "total_impressions": total_impressions,
                "total_engagement": total_engagement,
                "total_reach": total_reach,
                "avg_engagement_rate": total_engagement / max(total_reach, 1),
            },
            "platforms": platform_summaries,
            "synced_at": datetime.now().isoformat(),
        }

    async def _update_performance_metrics(self, aggregated: Dict):
        """Update performance metrics in database"""
        # In production, save to MongoDB
        self.logger.info(f"Updated metrics: {aggregated['summary']}")

    async def _identify_trends(self, aggregated: Dict) -> List[Dict]:
        """Identify performance trends"""
        trends = []

        summary = aggregated.get("summary", {})
        engagement_rate = summary.get("avg_engagement_rate", 0)

        # Check engagement thresholds
        thresholds = Config.ENGAGEMENT_THRESHOLDS

        if engagement_rate >= thresholds.get("excellent", 0.06):
            trends.append(
                {
                    "type": "positive",
                    "metric": "engagement_rate",
                    "message": "Excellent engagement rate!",
                    "value": engagement_rate,
                }
            )
        elif engagement_rate <= thresholds.get("poor", 0.015):
            trends.append(
                {
                    "type": "negative",
                    "metric": "engagement_rate",
                    "message": "Engagement rate needs improvement",
                    "value": engagement_rate,
                }
            )

        # Platform-specific trends
        for platform, data in aggregated.get("platforms", {}).items():
            if data["posts"] > 0:
                platform_rate = data["engagement"] / max(data["reach"], 1)
                if platform_rate > engagement_rate * 1.2:
                    trends.append(
                        {
                            "type": "insight",
                            "platform": platform,
                            "message": f"{platform.title()} outperforming average",
                            "value": platform_rate,
                        }
                    )

        return trends


def main():
    """Main entry point"""
    job = AnalyticsSyncJob()

    try:
        result = asyncio.run(job.run())
        print(f"Job completed: {result}")
    except Exception as e:
        print(f"Job failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
