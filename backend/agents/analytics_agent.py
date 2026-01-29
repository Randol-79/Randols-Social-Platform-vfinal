"""
Analytics Agent - Real-time performance tracking and analysis
Monitors engagement, sentiment, and provides actionable insights
"""

import asyncio
import random
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from utils.config import Config
from utils.logger import setup_logger


class AnalyticsAgent:
    """
    Analytics and performance monitoring agent.
    Tracks engagement, sentiment, and generates insights.
    """

    def __init__(self):
        self.logger = setup_logger("analytics_agent")
        self.performance_cache: Dict[str, Any] = {}
        self.baseline_metrics = self._load_baseline_metrics()
        self.status = "active"
        self.analyses_today = 0

    def _load_baseline_metrics(self) -> Dict[str, float]:
        """Load baseline performance metrics"""
        return {
            "instagram_engagement_rate": 0.042,
            "facebook_engagement_rate": 0.038,
            "tiktok_engagement_rate": 0.061,
            "youtube_engagement_rate": 0.029,
            "google_posts_engagement_rate": 0.025,
            "average_reach": 2500,
            "average_impressions": 5000,
            "conversion_rate": 0.025,
            "sentiment_score": 0.75,
        }

    async def analyze_performance(self, time_period: str = "7d") -> Dict[str, Any]:
        """Analyze recent performance and identify trends"""
        self.logger.info(f"Analyzing performance for period: {time_period}")
        self.analyses_today += 1

        try:
            # Get performance data
            performance_data = await self._get_performance_data(time_period)

            analysis = {
                "timestamp": datetime.now().isoformat(),
                "time_period": time_period,
                "overall_performance": self._calculate_overall_performance(performance_data),
                "platform_analysis": self._analyze_platforms(performance_data),
                "content_type_analysis": self._analyze_content_types(performance_data),
                "timing_analysis": self._analyze_timing(performance_data),
                "sentiment_analysis": await self._analyze_sentiment(performance_data),
                "trends": self._identify_trends(performance_data),
                "recommendations": [],
            }

            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)

            self.logger.info(
                f"Analysis completed: {len(analysis['recommendations'])} recommendations"
            )
            return analysis

        except Exception as e:
            self.logger.error(f"Error in performance analysis: {e}")
            return {"error": str(e)}

    async def _get_performance_data(self, time_period: str) -> Dict[str, Any]:
        """Retrieve performance data (mock data for demo)"""
        days = int(time_period.replace("d", "")) if "d" in time_period else 7

        # Generate mock performance data
        posts = []
        platforms = ["instagram", "facebook", "tiktok", "youtube"]
        content_types = [
            "morning_greeting",
            "daily_special",
            "crawfish_content",
            "event_promotion",
            "storytelling",
        ]

        for i in range(days * 4):  # ~4 posts per day
            platform = random.choice(platforms)
            base_engagement = self.baseline_metrics.get(f"{platform}_engagement_rate", 0.04)

            post = {
                "id": f"post_{i}",
                "platform": platform,
                "content_type": random.choice(content_types),
                "posting_time": f"{random.randint(8, 20):02d}:00",
                "posting_date": (
                    datetime.now() - timedelta(days=random.randint(0, days - 1))
                ).strftime("%Y-%m-%d"),
                "engagement_rate": max(0.01, random.gauss(base_engagement, 0.015)),
                "reach": int(random.gauss(2500, 800)),
                "impressions": int(random.gauss(5000, 1500)),
                "likes": int(random.gauss(100, 40)),
                "comments": int(random.gauss(12, 5)),
                "shares": int(random.gauss(8, 4)),
                "saves": int(random.gauss(15, 6)),
                "sentiment_score": random.uniform(0.6, 0.95),
                "authenticity_score": random.uniform(0.75, 0.98),
            }
            posts.append(post)

        return {
            "posts": posts,
            "platforms": platforms,
            "total_posts": len(posts),
            "date_range": {
                "start": (datetime.now() - timedelta(days=days)).isoformat(),
                "end": datetime.now().isoformat(),
            },
        }

    def _calculate_overall_performance(self, data: Dict) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        posts = data.get("posts", [])

        if not posts:
            return {"error": "No posts found"}

        engagement_rates = [p["engagement_rate"] for p in posts]
        reaches = [p["reach"] for p in posts]
        sentiment_scores = [p["sentiment_score"] for p in posts]
        authenticity_scores = [p["authenticity_score"] for p in posts]

        avg_engagement = statistics.mean(engagement_rates)

        return {
            "avg_engagement_rate": round(avg_engagement, 4),
            "engagement_trend": self._calculate_trend(engagement_rates),
            "avg_reach": round(statistics.mean(reaches)),
            "total_reach": sum(reaches),
            "avg_sentiment": round(statistics.mean(sentiment_scores), 3),
            "avg_authenticity": round(statistics.mean(authenticity_scores), 3),
            "total_posts": len(posts),
            "performance_grade": self._calculate_grade(avg_engagement),
            "vs_baseline": round(
                (avg_engagement / self.baseline_metrics["instagram_engagement_rate"] - 1) * 100, 1
            ),
        }

    def _analyze_platforms(self, data: Dict) -> Dict[str, Any]:
        """Analyze performance by platform"""
        posts = data.get("posts", [])
        platform_analysis = {}

        for platform in ["instagram", "facebook", "tiktok", "youtube"]:
            platform_posts = [p for p in posts if p["platform"] == platform]

            if platform_posts:
                engagement_rates = [p["engagement_rate"] for p in platform_posts]
                baseline = self.baseline_metrics.get(f"{platform}_engagement_rate", 0.04)
                avg_engagement = statistics.mean(engagement_rates)

                platform_analysis[platform] = {
                    "post_count": len(platform_posts),
                    "avg_engagement_rate": round(avg_engagement, 4),
                    "vs_baseline": round((avg_engagement / baseline - 1) * 100, 1),
                    "best_content_type": self._get_best_content_type(platform_posts),
                    "avg_reach": round(statistics.mean([p["reach"] for p in platform_posts])),
                    "trend": self._calculate_trend(engagement_rates),
                }

        return platform_analysis

    def _analyze_content_types(self, data: Dict) -> Dict[str, Any]:
        """Analyze performance by content type"""
        posts = data.get("posts", [])
        content_analysis = {}

        content_types = set(p["content_type"] for p in posts)

        for content_type in content_types:
            type_posts = [p for p in posts if p["content_type"] == content_type]

            if type_posts:
                engagement_rates = [p["engagement_rate"] for p in type_posts]

                content_analysis[content_type] = {
                    "post_count": len(type_posts),
                    "avg_engagement_rate": round(statistics.mean(engagement_rates), 4),
                    "avg_authenticity": round(
                        statistics.mean([p["authenticity_score"] for p in type_posts]), 3
                    ),
                    "best_platform": max(type_posts, key=lambda x: x["engagement_rate"])[
                        "platform"
                    ],
                    "trend": self._calculate_trend(engagement_rates),
                }

        # Sort by engagement rate
        content_analysis = dict(
            sorted(
                content_analysis.items(), key=lambda x: x[1]["avg_engagement_rate"], reverse=True
            )
        )

        return content_analysis

    def _analyze_timing(self, data: Dict) -> Dict[str, Any]:
        """Analyze optimal posting times"""
        posts = data.get("posts", [])

        time_windows = {
            "morning": {"start": 8, "end": 11, "posts": []},
            "lunch": {"start": 11, "end": 14, "posts": []},
            "afternoon": {"start": 14, "end": 17, "posts": []},
            "evening": {"start": 17, "end": 21, "posts": []},
        }

        for post in posts:
            hour = int(post["posting_time"].split(":")[0])
            for window_name, window in time_windows.items():
                if window["start"] <= hour < window["end"]:
                    window["posts"].append(post)
                    break

        timing_analysis = {}
        for window_name, window in time_windows.items():
            if window["posts"]:
                engagement_rates = [p["engagement_rate"] for p in window["posts"]]
                timing_analysis[window_name] = {
                    "post_count": len(window["posts"]),
                    "avg_engagement_rate": round(statistics.mean(engagement_rates), 4),
                    "time_range": f"{window['start']:02d}:00 - {window['end']:02d}:00",
                }

        # Find best time window
        if timing_analysis:
            best_window = max(timing_analysis.items(), key=lambda x: x[1]["avg_engagement_rate"])
            timing_analysis["recommended_window"] = best_window[0]

        return timing_analysis

    async def _analyze_sentiment(self, data: Dict) -> Dict[str, Any]:
        """Analyze sentiment of engagement"""
        posts = data.get("posts", [])

        if not posts:
            return {"error": "No posts to analyze"}

        sentiment_scores = [p["sentiment_score"] for p in posts]
        avg_sentiment = statistics.mean(sentiment_scores)

        # Categorize sentiment
        positive = len([s for s in sentiment_scores if s >= 0.7])
        neutral = len([s for s in sentiment_scores if 0.4 <= s < 0.7])
        negative = len([s for s in sentiment_scores if s < 0.4])

        return {
            "avg_sentiment_score": round(avg_sentiment, 3),
            "sentiment_distribution": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
            },
            "sentiment_trend": self._calculate_trend(sentiment_scores),
            "sentiment_grade": "Excellent"
            if avg_sentiment >= 0.8
            else "Good"
            if avg_sentiment >= 0.6
            else "Needs Attention",
        }

    def _identify_trends(self, data: Dict) -> Dict[str, Any]:
        """Identify performance trends"""
        posts = data.get("posts", [])

        if len(posts) < 2:
            return {"status": "insufficient_data"}

        # Sort by date
        sorted_posts = sorted(posts, key=lambda x: x["posting_date"])

        # Split into first and second half
        mid = len(sorted_posts) // 2
        first_half = sorted_posts[:mid]
        second_half = sorted_posts[mid:]

        first_half_engagement = statistics.mean([p["engagement_rate"] for p in first_half])
        second_half_engagement = statistics.mean([p["engagement_rate"] for p in second_half])

        change = ((second_half_engagement - first_half_engagement) / first_half_engagement) * 100

        return {
            "engagement_change": round(change, 1),
            "direction": "improving" if change > 5 else "declining" if change < -5 else "stable",
            "confidence": "high" if len(posts) >= 20 else "medium" if len(posts) >= 10 else "low",
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "insufficient_data"

        mid = len(values) // 2
        first_half = statistics.mean(values[:mid])
        second_half = statistics.mean(values[mid:])

        change = (second_half - first_half) / first_half if first_half > 0 else 0

        if change > 0.05:
            return "improving"
        elif change < -0.05:
            return "declining"
        return "stable"

    def _calculate_grade(self, engagement_rate: float) -> str:
        """Calculate performance grade"""
        thresholds = Config.ENGAGEMENT_THRESHOLDS

        if engagement_rate >= thresholds["excellent"]:
            return "A"
        elif engagement_rate >= thresholds["good"]:
            return "B"
        elif engagement_rate >= thresholds["average"]:
            return "C"
        return "D"

    def _get_best_content_type(self, posts: List[Dict]) -> str:
        """Get best performing content type"""
        if not posts:
            return "unknown"

        content_performance = {}
        for post in posts:
            ct = post["content_type"]
            if ct not in content_performance:
                content_performance[ct] = []
            content_performance[ct].append(post["engagement_rate"])

        best = max(content_performance.items(), key=lambda x: statistics.mean(x[1]))
        return best[0]

    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations: List[Dict] = []

        overall = analysis.get("overall_performance", {})
        platforms = analysis.get("platform_analysis", {})
        content = analysis.get("content_type_analysis", {})
        timing = analysis.get("timing_analysis", {})

        # Overall performance recommendations
        grade = overall.get("performance_grade", "C")
        if grade in ["C", "D"]:
            recommendations.append(
                {
                    "type": "performance",
                    "priority": "high",
                    "title": "Boost Overall Engagement",
                    "description": f"Current grade: {grade}. Engagement is below target.",
                    "actions": [
                        "Increase authentic Cajun content frequency",
                        "Add more storytelling posts about family traditions",
                        "Include more crawfish and zydeco content",
                    ],
                }
            )

        # Platform-specific recommendations
        for platform, data in platforms.items():
            if data.get("vs_baseline", 0) < -10:
                recommendations.append(
                    {
                        "type": "platform",
                        "priority": "medium",
                        "title": f"Improve {platform.title()} Performance",
                        "description": f"{platform.title()} is {abs(data['vs_baseline'])}% below baseline",
                        "actions": [
                            f"Post more {data.get('best_content_type', 'top')} content on {platform}",
                            f"Optimize posting times for {platform}",
                            "Increase video content on {platform}"
                            if platform in ["tiktok", "instagram"]
                            else f"Increase engagement with community on {platform}",
                        ],
                    }
                )

        # Timing recommendations
        if timing.get("recommended_window"):
            best_window = timing["recommended_window"]
            recommendations.append(
                {
                    "type": "timing",
                    "priority": "low",
                    "title": "Optimize Posting Schedule",
                    "description": f"Best performing time is {best_window}",
                    "actions": [
                        f"Schedule key posts during {best_window} window",
                        "Reduce posts during low-engagement periods",
                        "Test weekend posting times",
                    ],
                }
            )

        # Content type recommendations
        if content:
            best_content = list(content.keys())[0] if content else None
            if best_content:
                recommendations.append(
                    {
                        "type": "content",
                        "priority": "medium",
                        "title": "Leverage Best Content",
                        "description": f"'{best_content}' performs best",
                        "actions": [
                            f"Increase {best_content} frequency",
                            "Create variations of top-performing content",
                            "Cross-post successful content across platforms",
                        ],
                    }
                )

        return recommendations

    async def generate_recommendations(self) -> List[Dict]:
        """Public method to generate recommendations based on latest analysis"""
        analysis = await self.analyze_performance()
        if not analysis or "error" in analysis:
            return []
        # Use recommendations computed during analysis if present, otherwise generate now
        return analysis.get("recommendations") or self._generate_recommendations(analysis)

    async def get_platform_analytics(self) -> Dict[str, Any]:
        """Get current platform analytics"""
        return {
            "instagram": {
                "followers": 12500,
                "engagement_rate": 0.042,
                "posts_this_week": 14,
                "reach": 45000,
                "profile_visits": 890,
            },
            "facebook": {
                "page_likes": 8900,
                "engagement_rate": 0.038,
                "posts_this_week": 12,
                "reach": 32000,
                "page_views": 1200,
            },
            "tiktok": {
                "followers": 5600,
                "engagement_rate": 0.061,
                "videos_this_week": 8,
                "views": 125000,
                "profile_views": 2300,
            },
            "youtube": {
                "subscribers": 2100,
                "engagement_rate": 0.029,
                "videos_this_week": 2,
                "views": 8500,
                "watch_time_hours": 450,
            },
        }

    async def get_engagement_metrics(
        self, platform: str = "all", period: str = "7d"
    ) -> Dict[str, Any]:
        """Get engagement metrics"""
        data = await self._get_performance_data(period)

        if platform != "all":
            posts = [p for p in data["posts"] if p["platform"] == platform]
        else:
            posts = data["posts"]

        if not posts:
            return {"error": "No data found"}

        return {
            "period": period,
            "platform": platform,
            "total_posts": len(posts),
            "total_likes": sum(p["likes"] for p in posts),
            "total_comments": sum(p["comments"] for p in posts),
            "total_shares": sum(p["shares"] for p in posts),
            "total_saves": sum(p["saves"] for p in posts),
            "avg_engagement_rate": round(statistics.mean([p["engagement_rate"] for p in posts]), 4),
            "total_reach": sum(p["reach"] for p in posts),
        }

    async def get_sentiment_analysis(self) -> Dict[str, Any]:
        """Get sentiment analysis"""
        data = await self._get_performance_data("7d")
        return await self._analyze_sentiment(data)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": "Analytics Agent",
            "status": self.status,
            "health": "good",
            "analyses_today": self.analyses_today,
            "last_analysis": datetime.now().isoformat(),
            "uptime": "99.9%",
        }

    async def pause(self):
        """Pause the agent"""
        self.status = "paused"
        self.logger.info("Analytics Agent paused")

    async def resume(self):
        """Resume the agent"""
        self.status = "active"
        self.logger.info("Analytics Agent resumed")


# Test function
async def test_analytics_agent():
    agent = AnalyticsAgent()

    analysis = await agent.analyze_performance("7d")

    print("Overall Performance:")
    print(f"  Grade: {analysis['overall_performance'].get('performance_grade')}")
    print(f"  Avg Engagement: {analysis['overall_performance'].get('avg_engagement_rate')}")

    print("\nRecommendations:")
    for rec in analysis.get("recommendations", [])[:3]:
        print(f"  - [{rec['priority']}] {rec['title']}")


if __name__ == "__main__":
    asyncio.run(test_analytics_agent())
