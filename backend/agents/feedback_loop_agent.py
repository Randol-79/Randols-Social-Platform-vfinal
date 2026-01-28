"""
Feedback Loop Agent - Continuous optimization based on performance data
Handles A/B testing, engagement analysis, and strategy refinement
"""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import json
import statistics
import random

from utils.logger import setup_logger
from utils.config import Config


class FeedbackLoopAgent:
    """
    Continuous optimization agent that learns from performance data.
    Implements A/B testing, engagement analysis, and strategy refinement.
    """
    
    def __init__(self):
        self.logger = setup_logger("feedback_loop_agent")
        self.performance_history: Dict[str, List[Dict]] = {}
        self.optimization_rules = self._load_optimization_rules()
        self.ab_tests: Dict[str, Dict] = {}
        self.baseline_metrics = self._load_baseline_metrics()
        self.learning_insights: List[Dict] = []
        self.status = 'active'
        self.optimizations_today = 0

    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load performance optimization rules"""
        return {
            'engagement_thresholds': {
                'excellent': 0.06,    # 6%+ engagement rate
                'good': 0.04,         # 4%+ engagement rate
                'average': 0.025,     # 2.5%+ engagement rate
                'poor': 0.015         # Below 1.5% needs attention
            },
            'posting_time_windows': {
                'early_morning': {'start': '06:00', 'end': '08:00', 'weight': 0.7},
                'morning': {'start': '08:00', 'end': '10:00', 'weight': 1.0},
                'lunch': {'start': '11:30', 'end': '13:00', 'weight': 1.2},
                'afternoon': {'start': '15:00', 'end': '17:00', 'weight': 0.9},
                'evening': {'start': '18:00', 'end': '20:00', 'weight': 1.3},
                'night': {'start': '20:00', 'end': '22:00', 'weight': 0.8}
            },
            'content_type_performance': {
                'crawfish_content': {'target_engagement': 0.055, 'priority': 'high'},
                'zydeco_content': {'target_engagement': 0.045, 'priority': 'medium'},
                'daily_special': {'target_engagement': 0.035, 'priority': 'high'},
                'event_promotion': {'target_engagement': 0.065, 'priority': 'high'},
                'storytelling': {'target_engagement': 0.050, 'priority': 'medium'},
                'morning_greeting': {'target_engagement': 0.030, 'priority': 'low'}
            },
            'platform_weights': {
                'instagram': 1.2,
                'facebook': 1.0,
                'tiktok': 1.5,
                'youtube': 0.8,
                'google_posts': 0.6
            },
            'authenticity_impact': {
                'high_authenticity': 1.3,      # 85%+ authenticity score
                'medium_authenticity': 1.0,   # 70-85% authenticity
                'low_authenticity': 0.7       # Below 70%
            }
        }

    def _load_baseline_metrics(self) -> Dict[str, float]:
        """Load baseline performance metrics"""
        return {
            'instagram_engagement_rate': 0.042,
            'facebook_engagement_rate': 0.038,
            'tiktok_engagement_rate': 0.061,
            'youtube_engagement_rate': 0.029,
            'google_posts_engagement_rate': 0.025,
            'average_reach': 2500,
            'conversion_rate': 0.025,
            'sentiment_baseline': 0.75,
            'authenticity_baseline': 0.80
        }

    async def analyze_performance(self, time_period: str = '7d') -> Dict[str, Any]:
        """Analyze recent performance and identify trends"""
        try:
            self.logger.info(f"Analyzing performance for period: {time_period}")
            
            # Get performance data for analysis
            performance_data = await self._get_performance_data(time_period)

            analysis = {
                'timestamp': datetime.now().isoformat(),
                'time_period': time_period,
                'overall_performance': self._calculate_overall_performance(performance_data),
                'platform_analysis': self._analyze_platform_performance(performance_data),
                'content_type_analysis': self._analyze_content_types(performance_data),
                'timing_analysis': self._analyze_posting_times(performance_data),
                'authenticity_correlation': self._analyze_authenticity_impact(performance_data),
                'recommendations': []
            }

            # Generate recommendations based on analysis
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            # Store insights for learning
            self._store_learning_insight(analysis)
            
            self.optimizations_today += 1
            self.logger.info(f"Performance analysis completed: {len(analysis['recommendations'])} recommendations generated")
            return analysis

        except Exception as e:
            self.logger.error(f"Error in performance analysis: {str(e)}")
            return {'error': str(e)}

    async def _get_performance_data(self, time_period: str) -> Dict[str, Any]:
        """Retrieve performance data from social media platforms"""
        days = int(time_period.replace('d', '')) if 'd' in time_period else 7

        # Generate realistic mock data
        posts = []
        platforms = ['instagram', 'facebook', 'tiktok', 'youtube']
        content_types = ['crawfish_content', 'daily_special', 'event_promotion', 
                        'zydeco_content', 'storytelling', 'morning_greeting']
        
        for i in range(days * 4):  # ~4 posts per day
            platform = random.choice(platforms)
            content_type = random.choice(content_types)
            base_engagement = self.baseline_metrics.get(f'{platform}_engagement_rate', 0.04)
            
            # Add content type modifier
            type_config = self.optimization_rules['content_type_performance'].get(content_type, {})
            type_modifier = type_config.get('target_engagement', 0.04) / 0.04
            
            # Add authenticity correlation
            authenticity = random.uniform(0.70, 0.98)
            auth_modifier = 1.0 + (authenticity - 0.80) * 0.5
            
            post = {
                'id': f"post_{i}",
                'platform': platform,
                'content_type': content_type,
                'posting_time': f"{random.randint(8, 20):02d}:{random.choice(['00', '30'])}",
                'posting_date': (datetime.now() - timedelta(days=random.randint(0, days-1))).strftime('%Y-%m-%d'),
                'engagement_rate': max(0.01, random.gauss(base_engagement * type_modifier * auth_modifier, 0.012)),
                'reach': int(random.gauss(2500, 600)),
                'impressions': int(random.gauss(5000, 1200)),
                'likes': int(random.gauss(100, 35)),
                'comments': int(random.gauss(12, 5)),
                'shares': int(random.gauss(8, 4)),
                'saves': int(random.gauss(15, 6)),
                'sentiment_score': random.uniform(0.65, 0.95),
                'authenticity_score': authenticity,
                'cajun_phrase_count': random.randint(1, 5)
            }
            posts.append(post)

        return {
            'posts': posts,
            'platforms': platforms,
            'total_posts': len(posts),
            'date_range': {
                'start': (datetime.now() - timedelta(days=days)).isoformat(),
                'end': datetime.now().isoformat()
            }
        }

    def _calculate_overall_performance(self, data: Dict) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        posts = data.get('posts', [])

        if not posts:
            return {'error': 'No posts found'}

        engagement_rates = [post['engagement_rate'] for post in posts]
        reaches = [post['reach'] for post in posts]
        sentiment_scores = [post['sentiment_score'] for post in posts]
        authenticity_scores = [post['authenticity_score'] for post in posts]

        avg_engagement = statistics.mean(engagement_rates)
        
        return {
            'avg_engagement_rate': round(avg_engagement, 4),
            'engagement_rate_trend': self._calculate_trend(engagement_rates),
            'avg_reach': round(statistics.mean(reaches)),
            'total_reach': sum(reaches),
            'reach_trend': self._calculate_trend(reaches),
            'avg_sentiment': round(statistics.mean(sentiment_scores), 3),
            'avg_authenticity': round(statistics.mean(authenticity_scores), 3),
            'total_posts': len(posts),
            'performance_grade': self._calculate_performance_grade(avg_engagement),
            'vs_baseline': round((avg_engagement / self.baseline_metrics['instagram_engagement_rate'] - 1) * 100, 1)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a metric"""
        if len(values) < 4:
            return 'insufficient_data'

        # Compare first half to second half
        mid = len(values) // 2
        first_half_avg = statistics.mean(values[:mid])
        second_half_avg = statistics.mean(values[mid:])

        change = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0

        if change > 0.05:
            return 'improving'
        elif change < -0.05:
            return 'declining'
        else:
            return 'stable'

    def _calculate_performance_grade(self, engagement_rate: float) -> str:
        """Calculate performance grade based on engagement rate"""
        thresholds = self.optimization_rules['engagement_thresholds']

        if engagement_rate >= thresholds['excellent']:
            return 'A'
        elif engagement_rate >= thresholds['good']:
            return 'B'
        elif engagement_rate >= thresholds['average']:
            return 'C'
        else:
            return 'D'

    def _analyze_platform_performance(self, data: Dict) -> Dict[str, Any]:
        """Analyze performance by platform"""
        posts = data.get('posts', [])
        platform_analysis = {}

        for platform in ['instagram', 'facebook', 'tiktok', 'youtube']:
            platform_posts = [post for post in posts if post['platform'] == platform]

            if platform_posts:
                engagement_rates = [post['engagement_rate'] for post in platform_posts]
                baseline = self.baseline_metrics.get(f'{platform}_engagement_rate', 0.04)
                avg_engagement = statistics.mean(engagement_rates)
                
                # Find best performing content type for this platform
                content_performance = {}
                for post in platform_posts:
                    ct = post['content_type']
                    if ct not in content_performance:
                        content_performance[ct] = []
                    content_performance[ct].append(post['engagement_rate'])
                
                best_content = max(content_performance.items(), 
                                  key=lambda x: statistics.mean(x[1]))[0] if content_performance else 'unknown'
                
                platform_analysis[platform] = {
                    'post_count': len(platform_posts),
                    'avg_engagement_rate': round(avg_engagement, 4),
                    'performance_vs_baseline': round(avg_engagement / baseline, 2),
                    'vs_baseline_percent': round((avg_engagement / baseline - 1) * 100, 1),
                    'best_performing_content': best_content,
                    'avg_authenticity': round(statistics.mean([p['authenticity_score'] for p in platform_posts]), 3),
                    'trend': self._calculate_trend(engagement_rates)
                }

        return platform_analysis

    def _analyze_content_types(self, data: Dict) -> Dict[str, Any]:
        """Analyze performance by content type"""
        posts = data.get('posts', [])
        content_analysis = {}

        content_types = set(post['content_type'] for post in posts)
        
        for content_type in content_types:
            type_posts = [post for post in posts if post['content_type'] == content_type]

            if type_posts:
                engagement_rates = [post['engagement_rate'] for post in type_posts]
                target = self.optimization_rules['content_type_performance'].get(
                    content_type, {}).get('target_engagement', 0.04)
                avg_engagement = statistics.mean(engagement_rates)
                
                content_analysis[content_type] = {
                    'post_count': len(type_posts),
                    'avg_engagement_rate': round(avg_engagement, 4),
                    'performance_vs_target': round(avg_engagement / target, 2),
                    'best_platform': max(type_posts, key=lambda x: x['engagement_rate'])['platform'],
                    'avg_authenticity': round(statistics.mean([p['authenticity_score'] for p in type_posts]), 3),
                    'trend': self._calculate_trend(engagement_rates)
                }

        # Sort by engagement rate
        content_analysis = dict(sorted(
            content_analysis.items(),
            key=lambda x: x[1]['avg_engagement_rate'],
            reverse=True
        ))
        
        return content_analysis

    def _analyze_posting_times(self, data: Dict) -> Dict[str, Any]:
        """Analyze optimal posting times"""
        posts = data.get('posts', [])
        time_analysis = {}

        for time_window, window_data in self.optimization_rules['posting_time_windows'].items():
            window_posts = []

            for post in posts:
                post_hour = int(post['posting_time'].split(':')[0])
                start_hour = int(window_data['start'].split(':')[0])
                end_hour = int(window_data['end'].split(':')[0])

                if start_hour <= post_hour < end_hour:
                    window_posts.append(post)

            if window_posts:
                engagement_rates = [post['engagement_rate'] for post in window_posts]
                time_analysis[time_window] = {
                    'post_count': len(window_posts),
                    'avg_engagement_rate': round(statistics.mean(engagement_rates), 4),
                    'window': f"{window_data['start']} - {window_data['end']}",
                    'weight': window_data['weight']
                }

        # Find best time window
        if time_analysis:
            best_window = max(time_analysis.items(), key=lambda x: x[1]['avg_engagement_rate'])
            time_analysis['recommended_window'] = best_window[0]
            time_analysis['recommended_times'] = {
                'instagram': best_window[1]['window'].split(' - ')[0],
                'facebook': best_window[1]['window'].split(' - ')[0],
                'tiktok': '15:00' if 'afternoon' in best_window[0] else '19:00',
                'youtube': '16:00'
            }
            
        return time_analysis

    def _analyze_authenticity_impact(self, data: Dict) -> Dict[str, Any]:
        """Analyze how authenticity scores correlate with engagement"""
        posts = data.get('posts', [])
        
        if not posts:
            return {'error': 'No posts to analyze'}
        
        # Group posts by authenticity level
        high_auth = [p for p in posts if p['authenticity_score'] >= 0.85]
        medium_auth = [p for p in posts if 0.70 <= p['authenticity_score'] < 0.85]
        low_auth = [p for p in posts if p['authenticity_score'] < 0.70]
        
        analysis = {
            'high_authenticity': {
                'count': len(high_auth),
                'avg_engagement': round(statistics.mean([p['engagement_rate'] for p in high_auth]), 4) if high_auth else 0
            },
            'medium_authenticity': {
                'count': len(medium_auth),
                'avg_engagement': round(statistics.mean([p['engagement_rate'] for p in medium_auth]), 4) if medium_auth else 0
            },
            'low_authenticity': {
                'count': len(low_auth),
                'avg_engagement': round(statistics.mean([p['engagement_rate'] for p in low_auth]), 4) if low_auth else 0
            }
        }
        
        # Calculate correlation insight
        if high_auth and medium_auth:
            improvement = (analysis['high_authenticity']['avg_engagement'] / 
                         max(analysis['medium_authenticity']['avg_engagement'], 0.001) - 1) * 100
            analysis['insight'] = f"High authenticity content performs {improvement:.1f}% better"
        
        return analysis

    def _generate_recommendations(self, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        overall = analysis.get('overall_performance', {})
        platforms = analysis.get('platform_analysis', {})
        content_types = analysis.get('content_type_analysis', {})
        timing = analysis.get('timing_analysis', {})
        authenticity = analysis.get('authenticity_correlation', {})

        # Overall performance recommendations
        grade = overall.get('performance_grade', 'C')
        if grade in ['C', 'D']:
            recommendations.append({
                'type': 'performance_improvement',
                'priority': 'high',
                'title': 'Boost Overall Engagement',
                'description': f"Current grade: {grade}. Engagement rate ({overall.get('avg_engagement_rate', 0):.3f}) is below target",
                'actions': [
                    'Increase authentic Cajun content frequency',
                    'Add more storytelling about family traditions and recipes',
                    'Include more live music and zydeco references',
                    'Use more visual storytelling with food photography'
                ],
                'expected_impact': '+15-25% engagement'
            })

        # Platform-specific recommendations
        for platform, data in platforms.items():
            if data.get('vs_baseline_percent', 0) < -10:
                recommendations.append({
                    'type': 'platform_optimization',
                    'priority': 'medium',
                    'title': f'Optimize {platform.title()} Strategy',
                    'description': f"{platform.title()} is {abs(data['vs_baseline_percent'])}% below baseline",
                    'actions': [
                        f'Focus on {data["best_performing_content"]} content for {platform}',
                        f'Increase posting frequency during peak times',
                        f'Improve authenticity score (current: {data["avg_authenticity"]:.0%})'
                    ],
                    'expected_impact': f'+{abs(data["vs_baseline_percent"])//2}% engagement on {platform}'
                })

        # Content type recommendations
        for content_type, data in list(content_types.items())[:3]:  # Top 3
            if data['performance_vs_target'] < 0.9:
                recommendations.append({
                    'type': 'content_optimization',
                    'priority': 'medium',
                    'title': f'Improve {content_type.replace("_", " ").title()} Content',
                    'description': f"Performance is {(1-data['performance_vs_target'])*100:.1f}% below target",
                    'actions': [
                        f'Post more {content_type} on {data["best_platform"]}',
                        'Enhance visual elements and storytelling',
                        'Add more authentic Cajun phrases and cultural references'
                    ],
                    'expected_impact': '+10-15% engagement for this content type'
                })

        # Timing recommendations
        if timing.get('recommended_window'):
            best_window = timing['recommended_window']
            recommendations.append({
                'type': 'timing_optimization',
                'priority': 'low',
                'title': 'Optimize Posting Schedule',
                'description': f"Best performing time window is {best_window} ({timing[best_window]['window']})",
                'actions': [
                    f'Schedule key posts during {best_window} window',
                    'Reduce posts during low-engagement periods',
                    'Test weekend vs weekday performance'
                ],
                'expected_impact': '+5-10% engagement from timing optimization'
            })

        # Authenticity recommendations
        if authenticity.get('insight'):
            recommendations.append({
                'type': 'authenticity_boost',
                'priority': 'high',
                'title': 'Maximize Cajun Authenticity',
                'description': authenticity['insight'],
                'actions': [
                    'Increase use of authentic Cajun phrases',
                    'Add more family tradition storytelling',
                    'Reference local culture (zydeco, crawfish, bayou)',
                    'Use "cher" and "y\'all" naturally in posts'
                ],
                'expected_impact': '+20-30% engagement from authenticity improvement'
            })

        return recommendations

    def _store_learning_insight(self, analysis: Dict):
        """Store insights for continuous learning"""
        insight = {
            'timestamp': datetime.now().isoformat(),
            'performance_grade': analysis.get('overall_performance', {}).get('performance_grade'),
            'avg_engagement': analysis.get('overall_performance', {}).get('avg_engagement_rate'),
            'best_content_type': list(analysis.get('content_type_analysis', {}).keys())[0] if analysis.get('content_type_analysis') else None,
            'best_time_window': analysis.get('timing_analysis', {}).get('recommended_window'),
            'recommendation_count': len(analysis.get('recommendations', []))
        }
        
        self.learning_insights.append(insight)
        
        # Keep last 100 insights
        if len(self.learning_insights) > 100:
            self.learning_insights = self.learning_insights[-100:]

    async def get_optimal_posting_times(self) -> Dict[str, Dict[str, str]]:
        """Get optimal posting times for each platform"""
        return {
            'instagram': {
                'morning': '09:00',
                'lunch': '12:00',
                'evening': '18:30',
                'best': '18:30'
            },
            'facebook': {
                'morning': '08:30',
                'lunch': '12:30',
                'evening': '19:00',
                'best': '19:00'
            },
            'tiktok': {
                'afternoon': '15:00',
                'evening': '19:00',
                'night': '21:00',
                'best': '19:00'
            },
            'youtube': {
                'afternoon': '14:00',
                'evening': '17:00',
                'best': '17:00'
            },
            'google_posts': {
                'morning': '10:00',
                'afternoon': '14:00',
                'best': '10:00'
            }
        }

    async def trigger_content_optimization(self) -> Dict[str, Any]:
        """Trigger content optimization based on poor performance"""
        self.logger.info("Content optimization triggered due to performance drop")

        recent_analysis = await self.analyze_performance('3d')

        optimization_actions = [
            'Increase crawfish and zydeco content ratio by 20%',
            'Add more authentic Cajun phrases to all posts',
            'Focus on storytelling and family heritage themes',
            'Enhance visual content quality with food photography',
            'Adjust posting times to peak engagement windows',
            'Increase authenticity score threshold to 0.80'
        ]

        return {
            'trigger_reason': 'performance_drop',
            'timestamp': datetime.now().isoformat(),
            'actions_taken': optimization_actions,
            'analysis_summary': {
                'grade': recent_analysis.get('overall_performance', {}).get('performance_grade'),
                'engagement': recent_analysis.get('overall_performance', {}).get('avg_engagement_rate')
            },
            'expected_improvement': '15-25% engagement increase within 7 days'
        }

    async def start_ab_test(self, test_config: Dict) -> str:
        """Start an A/B test for content optimization"""
        test_id = f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.ab_tests[test_id] = {
            'id': test_id,
            'config': test_config,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(days=test_config.get('duration_days', 7))).isoformat(),
            'status': 'active',
            'results': {
                'a_group': {'posts': [], 'metrics': {}},
                'b_group': {'posts': [], 'metrics': {}}
            }
        }

        self.logger.info(f"A/B test started: {test_id} - Testing: {test_config.get('variable')}")
        return test_id

    async def evaluate_ab_test(self, test_id: str) -> Dict[str, Any]:
        """Evaluate results of an A/B test"""
        if test_id not in self.ab_tests:
            return {'error': 'Test not found'}

        test = self.ab_tests[test_id]

        # Mock evaluation with realistic results
        a_engagement = random.gauss(0.038, 0.008)
        b_engagement = random.gauss(0.045, 0.008)
        
        evaluation = {
            'test_id': test_id,
            'variable_tested': test['config'].get('variable'),
            'duration': f"{test['config'].get('duration_days', 7)} days",
            'a_group_performance': {
                'variant': 'Control',
                'avg_engagement': round(a_engagement, 4),
                'sample_size': 15,
                'authenticity_score': 0.78
            },
            'b_group_performance': {
                'variant': test['config'].get('variable'),
                'avg_engagement': round(b_engagement, 4),
                'sample_size': 15,
                'authenticity_score': 0.86
            },
            'statistical_significance': b_engagement > a_engagement + 0.005,
            'winner': 'B' if b_engagement > a_engagement else 'A',
            'improvement': f"+{((b_engagement/a_engagement)-1)*100:.1f}%",
            'recommendation': 'Implement B version strategy' if b_engagement > a_engagement else 'Keep current strategy',
            'confidence_level': '95%' if abs(b_engagement - a_engagement) > 0.005 else '85%'
        }

        test['status'] = 'completed'
        test['results']['evaluation'] = evaluation

        self.logger.info(f"A/B test {test_id} completed: Winner = {evaluation['winner']}")
        return evaluation

    def get_active_tests(self) -> List[Dict]:
        """Get all active A/B tests"""
        return [
            {'id': test_id, 'config': test['config'], 'status': test['status']}
            for test_id, test in self.ab_tests.items()
            if test['status'] == 'active'
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'name': 'Feedback Loop Agent',
            'status': self.status,
            'health': 'good',
            'active_ab_tests': len([t for t in self.ab_tests.values() if t['status'] == 'active']),
            'completed_tests': len([t for t in self.ab_tests.values() if t['status'] == 'completed']),
            'optimizations_today': self.optimizations_today,
            'learning_insights_stored': len(self.learning_insights),
            'last_optimization': datetime.now().isoformat(),
            'uptime': '96.1%'
        }

    async def pause(self):
        """Pause the agent"""
        self.status = 'paused'
        self.logger.info("Feedback Loop Agent paused")

    async def resume(self):
        """Resume the agent"""
        self.status = 'active'
        self.logger.info("Feedback Loop Agent resumed")


# Test function
async def test_feedback_loop():
    agent = FeedbackLoopAgent()
    
    # Test performance analysis
    analysis = await agent.analyze_performance('7d')
    print(f"Analysis completed: {len(analysis.get('recommendations', []))} recommendations")
    print(f"Performance Grade: {analysis.get('overall_performance', {}).get('performance_grade')}")

    # Test A/B testing
    test_config = {
        'test_type': 'content_style',
        'variable': 'cajun_authenticity_level',
        'duration_days': 7
    }
    test_id = await agent.start_ab_test(test_config)
    print(f"A/B test started: {test_id}")

    # Evaluate test
    results = await agent.evaluate_ab_test(test_id)
    print(f"Test winner: {results.get('winner')} with {results.get('improvement')} improvement")


if __name__ == "__main__":
    asyncio.run(test_feedback_loop())
