"""
Weekly Report Job
Runs every Monday morning to generate and send weekly performance report
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import aiohttp

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.logger import setup_logger
from agents.analytics_agent import AnalyticsAgent
from agents.feedback_loop_agent import FeedbackLoopAgent


class WeeklyReportJob:
    """Weekly performance report generation job"""
    
    def __init__(self):
        self.logger = setup_logger("weekly_report_job")
        self.analytics_agent = None
        self.feedback_agent = None
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    def _initialize(self):
        """Initialize agents"""
        if self.analytics_agent is None:
            self.analytics_agent = AnalyticsAgent()
        if self.feedback_agent is None:
            self.feedback_agent = FeedbackLoopAgent()
    
    async def run(self):
        """Execute weekly report generation"""
        start_time = datetime.now()
        week_start = start_time - timedelta(days=7)
        
        self.logger.info("=" * 50)
        self.logger.info("Weekly Report Job Starting")
        self.logger.info(f"Report period: {week_start.date()} to {start_time.date()}")
        self.logger.info("=" * 50)
        
        try:
            self._initialize()
            
            # Step 1: Collect weekly data
            weekly_data = await self._collect_weekly_data(week_start, start_time)
            
            # Step 2: Analyze performance
            performance = await self._analyze_performance(weekly_data)
            
            # Step 3: Get AI recommendations
            recommendations = await self._get_recommendations(performance)
            
            # Step 4: Generate report
            report = self._generate_report(weekly_data, performance, recommendations)
            
            # Step 5: Send notifications
            await self._send_slack_report(report)
            await self._send_email_report(report)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            self.logger.info("=" * 50)
            self.logger.info("Weekly Report Complete")
            self.logger.info(f"Duration: {duration:.2f}s")
            self.logger.info("=" * 50)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Weekly report failed: {str(e)}")
            await self._send_error_notification(str(e))
            raise
    
    async def _collect_weekly_data(self, start: datetime, end: datetime) -> Dict:
        """Collect data for the week"""
        return {
            'period': {
                'start': start.isoformat(),
                'end': end.isoformat()
            },
            'posts': await self._get_weekly_posts(start, end),
            'engagement': await self._get_weekly_engagement(start, end),
            'content_types': await self._get_content_breakdown(start, end),
            'platform_performance': await self._get_platform_performance(start, end),
            'top_posts': await self._get_top_posts(start, end),
            'audience_growth': await self._get_audience_growth(start, end)
        }
    
    async def _get_weekly_posts(self, start: datetime, end: datetime) -> Dict:
        """Get weekly post statistics"""
        # Mock data - integrate with database in production
        return {
            'total': 28,
            'by_day': {
                'monday': 4, 'tuesday': 4, 'wednesday': 4,
                'thursday': 4, 'friday': 5, 'saturday': 5, 'sunday': 2
            },
            'by_platform': {
                'instagram': 10, 'facebook': 10, 'tiktok': 4,
                'youtube': 2, 'google_posts': 2
            }
        }
    
    async def _get_weekly_engagement(self, start: datetime, end: datetime) -> Dict:
        """Get weekly engagement metrics"""
        return {
            'total_impressions': 45000,
            'total_reach': 32000,
            'total_engagement': 2100,
            'engagement_rate': 0.047,
            'vs_last_week': {
                'impressions_change': 0.12,
                'reach_change': 0.08,
                'engagement_change': 0.15
            }
        }
    
    async def _get_content_breakdown(self, start: datetime, end: datetime) -> Dict:
        """Get content type performance breakdown"""
        return {
            'morning_greeting': {'posts': 7, 'avg_engagement': 0.052},
            'daily_special': {'posts': 7, 'avg_engagement': 0.065},
            'evening_event': {'posts': 4, 'avg_engagement': 0.048},
            'crawfish_education': {'posts': 5, 'avg_engagement': 0.071},
            'storytelling': {'posts': 3, 'avg_engagement': 0.058},
            'event_promotion': {'posts': 2, 'avg_engagement': 0.044}
        }
    
    async def _get_platform_performance(self, start: datetime, end: datetime) -> Dict:
        """Get platform-specific performance"""
        return {
            'instagram': {
                'posts': 10,
                'impressions': 18000,
                'engagement_rate': 0.051,
                'top_time': '12:00',
                'growth': 0.08
            },
            'facebook': {
                'posts': 10,
                'impressions': 15000,
                'engagement_rate': 0.042,
                'top_time': '17:00',
                'growth': 0.05
            },
            'tiktok': {
                'posts': 4,
                'views': 8500,
                'engagement_rate': 0.075,
                'top_time': '19:00',
                'growth': 0.22
            },
            'youtube': {
                'posts': 2,
                'views': 2800,
                'watch_time_hours': 45,
                'growth': 0.03
            },
            'google_posts': {
                'posts': 2,
                'views': 700,
                'clicks': 85,
                'growth': 0.01
            }
        }
    
    async def _get_top_posts(self, start: datetime, end: datetime) -> List[Dict]:
        """Get top performing posts"""
        return [
            {
                'id': 'post_001',
                'platform': 'tiktok',
                'type': 'crawfish_education',
                'engagement_rate': 0.092,
                'views': 3200,
                'preview': "Fresh mudbugs from local waters..."
            },
            {
                'id': 'post_002',
                'platform': 'instagram',
                'type': 'daily_special',
                'engagement_rate': 0.078,
                'impressions': 2400,
                'preview': "Today's special: Gulf Shrimp Étouffée..."
            },
            {
                'id': 'post_003',
                'platform': 'facebook',
                'type': 'evening_event',
                'engagement_rate': 0.065,
                'impressions': 1800,
                'preview': "Zydeco Night this Friday!"
            }
        ]
    
    async def _get_audience_growth(self, start: datetime, end: datetime) -> Dict:
        """Get audience growth metrics"""
        return {
            'instagram': {'current': 5420, 'gained': 180, 'growth_pct': 0.034},
            'facebook': {'current': 8950, 'gained': 120, 'growth_pct': 0.014},
            'tiktok': {'current': 1250, 'gained': 280, 'growth_pct': 0.224},
            'youtube': {'current': 485, 'gained': 25, 'growth_pct': 0.052}
        }
    
    async def _analyze_performance(self, data: Dict) -> Dict:
        """Analyze weekly performance"""
        engagement = data['engagement']
        thresholds = Config.ENGAGEMENT_THRESHOLDS
        
        # Determine overall rating
        rate = engagement['engagement_rate']
        if rate >= thresholds['excellent']:
            rating = 'Excellent'
            rating_emoji = '🌟'
        elif rate >= thresholds['good']:
            rating = 'Good'
            rating_emoji = '✅'
        elif rate >= thresholds['average']:
            rating = 'Average'
            rating_emoji = '📊'
        else:
            rating = 'Needs Improvement'
            rating_emoji = '⚠️'
        
        # Best performing platform
        platforms = data['platform_performance']
        best_platform = max(platforms.items(), 
                          key=lambda x: x[1].get('engagement_rate', 0))
        
        # Best content type
        content_types = data['content_types']
        best_content = max(content_types.items(),
                          key=lambda x: x[1].get('avg_engagement', 0))
        
        return {
            'overall_rating': rating,
            'rating_emoji': rating_emoji,
            'engagement_rate': rate,
            'vs_target': rate / thresholds['good'],
            'best_platform': {
                'name': best_platform[0],
                'engagement_rate': best_platform[1]['engagement_rate']
            },
            'best_content_type': {
                'name': best_content[0],
                'engagement_rate': best_content[1]['avg_engagement']
            },
            'growth_leader': 'tiktok',
            'improvement_areas': self._identify_improvement_areas(data)
        }
    
    def _identify_improvement_areas(self, data: Dict) -> List[str]:
        """Identify areas needing improvement"""
        areas = []
        
        platforms = data['platform_performance']
        for platform, metrics in platforms.items():
            if metrics.get('engagement_rate', 0) < 0.03:
                areas.append(f"Improve {platform} engagement")
        
        content = data['content_types']
        for content_type, metrics in content.items():
            if metrics.get('avg_engagement', 0) < 0.04:
                areas.append(f"Optimize {content_type.replace('_', ' ')} content")
        
        return areas[:3]  # Top 3 improvements
    
    async def _get_recommendations(self, performance: Dict) -> List[Dict]:
        """Get AI-powered recommendations"""
        recommendations = []
        
        # Based on performance analysis
        if performance['best_platform']['name'] == 'tiktok':
            recommendations.append({
                'priority': 'high',
                'action': 'Increase TikTok posting frequency',
                'reason': 'TikTok showing highest engagement and growth',
                'expected_impact': '+15% overall engagement'
            })
        
        if 'crawfish_education' in performance['best_content_type']['name']:
            recommendations.append({
                'priority': 'high',
                'action': 'Create more educational crawfish content',
                'reason': 'Educational content resonates with audience',
                'expected_impact': '+10% engagement rate'
            })
        
        for area in performance['improvement_areas']:
            recommendations.append({
                'priority': 'medium',
                'action': area,
                'reason': 'Below target performance',
                'expected_impact': 'Variable'
            })
        
        return recommendations
    
    def _generate_report(self, data: Dict, performance: Dict, 
                        recommendations: List[Dict]) -> Dict:
        """Generate the weekly report"""
        return {
            'type': 'weekly_report',
            'generated_at': datetime.now().isoformat(),
            'period': data['period'],
            'summary': {
                'rating': performance['overall_rating'],
                'rating_emoji': performance['rating_emoji'],
                'total_posts': data['posts']['total'],
                'total_impressions': data['engagement']['total_impressions'],
                'engagement_rate': performance['engagement_rate'],
                'vs_last_week': data['engagement']['vs_last_week']
            },
            'highlights': {
                'best_platform': performance['best_platform'],
                'best_content': performance['best_content_type'],
                'top_posts': data['top_posts'][:3],
                'growth_leader': {
                    'platform': 'TikTok',
                    'growth': data['audience_growth']['tiktok']['growth_pct']
                }
            },
            'detailed_metrics': {
                'posts': data['posts'],
                'engagement': data['engagement'],
                'content_types': data['content_types'],
                'platform_performance': data['platform_performance'],
                'audience_growth': data['audience_growth']
            },
            'recommendations': recommendations,
            'improvement_areas': performance['improvement_areas']
        }
    
    async def _send_slack_report(self, report: Dict):
        """Send report to Slack"""
        if not self.slack_webhook:
            self.logger.warning("Slack webhook not configured")
            return
        
        summary = report['summary']
        highlights = report['highlights']
        
        # Format Slack message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Weekly Marketing Report {summary['rating_emoji']}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Overall Rating:* {summary['rating']}\n"
                           f"*Period:* {report['period']['start'][:10]} to {report['period']['end'][:10]}"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Posts:*\n{summary['total_posts']}"},
                    {"type": "mrkdwn", "text": f"*Impressions:*\n{summary['total_impressions']:,}"},
                    {"type": "mrkdwn", "text": f"*Engagement Rate:*\n{summary['engagement_rate']:.1%}"},
                    {"type": "mrkdwn", "text": f"*vs Last Week:*\n+{summary['vs_last_week']['engagement_change']:.0%}"}
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🏆 Top Performer:* {highlights['best_platform']['name'].title()} "
                           f"({highlights['best_platform']['engagement_rate']:.1%} engagement)\n"
                           f"*📈 Fastest Growing:* {highlights['growth_leader']['platform']} "
                           f"(+{highlights['growth_leader']['growth']:.0%})"
                }
            }
        ]
        
        # Add recommendations
        if report['recommendations']:
            rec_text = "*📋 This Week's Recommendations:*\n"
            for rec in report['recommendations'][:3]:
                rec_text += f"• {rec['action']}\n"
            
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": rec_text}
            })
        
        payload = {"blocks": blocks}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook, json=payload) as response:
                    if response.status == 200:
                        self.logger.info("Slack report sent successfully")
                    else:
                        self.logger.error(f"Slack send failed: {response.status}")
        except Exception as e:
            self.logger.error(f"Failed to send Slack report: {str(e)}")
    
    async def _send_email_report(self, report: Dict):
        """Send report via email"""
        # Integrate with email service (SendGrid, SES, etc.)
        self.logger.info("Email report would be sent here")
    
    async def _send_error_notification(self, error: str):
        """Send error notification"""
        if self.slack_webhook:
            payload = {
                "text": f"❌ Weekly Report Job Failed\n```{error}```"
            }
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(self.slack_webhook, json=payload)
            except Exception as e:
                self.logger.error(f"Failed to send error notification: {str(e)}")


def main():
    """Main entry point"""
    job = WeeklyReportJob()
    
    try:
        result = asyncio.run(job.run())
        print(f"Report generated: {result['summary']['rating']}")
    except Exception as e:
        print(f"Job failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
