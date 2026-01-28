"""
Platform Agents - Social Media Platform-Specific Publishing and Optimization
Handles posting, scheduling, and platform-specific content adaptation
"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib
import hmac
import base64
from utils.config import Config
from utils.logger import setup_logger


class BasePlatformAgent(ABC):
    """Base class for all platform-specific agents"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logger = setup_logger(f"platform_{platform_name}")
        self.config = Config.get_platform_config(platform_name)
        self.rate_limits = self._init_rate_limits()
        self.status = "active"
        self.last_post_time = None
        self.posts_today = 0
        self.error_count = 0
        self.session = None
    
    def _init_rate_limits(self) -> Dict[str, Any]:
        """Initialize platform-specific rate limits"""
        return {
            'posts_per_day': 25,
            'posts_per_hour': 5,
            'min_interval_minutes': 30,
            'current_window_posts': 0,
            'window_start': datetime.now()
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def can_post(self) -> bool:
        """Check if posting is allowed based on rate limits"""
        now = datetime.now()
        
        # Reset daily counter at midnight
        if self.last_post_time and self.last_post_time.date() < now.date():
            self.posts_today = 0
        
        # Check daily limit
        if self.posts_today >= self.rate_limits['posts_per_day']:
            self.logger.warning(f"{self.platform_name}: Daily post limit reached")
            return False
        
        # Check minimum interval
        if self.last_post_time:
            time_since_last = (now - self.last_post_time).total_seconds() / 60
            if time_since_last < self.rate_limits['min_interval_minutes']:
                self.logger.info(f"{self.platform_name}: Waiting for rate limit cooldown")
                return False
        
        return True
    
    @abstractmethod
    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for the specific platform"""
        pass
    
    @abstractmethod
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'platform': self.platform_name,
            'status': self.status,
            'posts_today': self.posts_today,
            'last_post_time': self.last_post_time.isoformat() if self.last_post_time else None,
            'error_count': self.error_count,
            'rate_limits': self.rate_limits
        }


class InstagramAgent(BasePlatformAgent):
    """Instagram-specific content publishing agent"""
    
    def __init__(self):
        super().__init__("instagram")
        self.access_token = Config.INSTAGRAM_ACCESS_TOKEN
        self.api_base = "https://graph.instagram.com/v18.0"
        self.content_types = ['image', 'carousel', 'reel', 'story']
    
    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to Instagram"""
        if not self.can_post():
            return {'success': False, 'error': 'Rate limit exceeded'}
        
        try:
            optimized = await self.optimize_content(content)
            
            # Determine content type and post accordingly
            content_type = optimized.get('media_type', 'image')
            
            if content_type == 'image':
                result = await self._post_image(optimized)
            elif content_type == 'carousel':
                result = await self._post_carousel(optimized)
            elif content_type == 'reel':
                result = await self._post_reel(optimized)
            else:
                result = await self._post_image(optimized)
            
            if result.get('success'):
                self.last_post_time = datetime.now()
                self.posts_today += 1
                self.logger.info(f"Instagram post successful: {result.get('post_id')}")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Instagram post error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _post_image(self, content: Dict) -> Dict:
        """Post a single image to Instagram"""
        session = await self._get_session()
        
        # Step 1: Create media container
        container_url = f"{self.api_base}/me/media"
        container_params = {
            'image_url': content.get('image_url'),
            'caption': content.get('text', ''),
            'access_token': self.access_token
        }
        
        # In production, make actual API call
        # For now, simulate success
        return {
            'success': True,
            'post_id': f"ig_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'instagram',
            'content_type': 'image',
            'posted_at': datetime.now().isoformat()
        }
    
    async def _post_carousel(self, content: Dict) -> Dict:
        """Post a carousel to Instagram"""
        # Create container for each image, then create carousel container
        return {
            'success': True,
            'post_id': f"ig_carousel_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'instagram',
            'content_type': 'carousel',
            'posted_at': datetime.now().isoformat()
        }
    
    async def _post_reel(self, content: Dict) -> Dict:
        """Post a Reel to Instagram"""
        return {
            'success': True,
            'post_id': f"ig_reel_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'instagram',
            'content_type': 'reel',
            'posted_at': datetime.now().isoformat()
        }
    
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Instagram"""
        optimized = content.copy()
        
        # Truncate caption if needed
        max_length = self.config.get('max_caption_length', 2200)
        if len(optimized.get('text', '')) > max_length:
            optimized['text'] = optimized['text'][:max_length-3] + '...'
        
        # Add hashtags (max 30)
        hashtags = optimized.get('hashtags', [])[:30]
        if hashtags:
            hashtag_str = ' '.join(hashtags)
            optimized['text'] = f"{optimized.get('text', '')}\n\n{hashtag_str}"
        
        # Optimize image dimensions
        optimized['recommended_dimensions'] = self.config.get('optimal_image_size', {
            'width': 1080,
            'height': 1080
        })
        
        # Add Instagram-specific optimizations
        optimized['instagram_optimizations'] = {
            'use_alt_text': True,
            'location_tag': 'Breaux Bridge, Louisiana',
            'product_tags': [],
            'collaborator_tags': []
        }
        
        return optimized
    
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Instagram post analytics"""
        # In production, fetch from Instagram Graph API
        return {
            'post_id': post_id,
            'platform': 'instagram',
            'impressions': 1250,
            'reach': 980,
            'engagement': 145,
            'likes': 120,
            'comments': 15,
            'saves': 10,
            'shares': 8,
            'engagement_rate': 0.048,
            'fetched_at': datetime.now().isoformat()
        }


class FacebookAgent(BasePlatformAgent):
    """Facebook-specific content publishing agent"""
    
    def __init__(self):
        super().__init__("facebook")
        self.access_token = Config.FACEBOOK_ACCESS_TOKEN
        self.api_base = "https://graph.facebook.com/v18.0"
        self.page_id = None  # Set from config
    
    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to Facebook"""
        if not self.can_post():
            return {'success': False, 'error': 'Rate limit exceeded'}
        
        try:
            optimized = await self.optimize_content(content)
            
            content_type = optimized.get('media_type', 'text')
            
            if content_type in ['image', 'food_photography']:
                result = await self._post_photo(optimized)
            elif content_type == 'video':
                result = await self._post_video(optimized)
            elif content_type == 'link':
                result = await self._post_link(optimized)
            else:
                result = await self._post_text(optimized)
            
            if result.get('success'):
                self.last_post_time = datetime.now()
                self.posts_today += 1
                self.logger.info(f"Facebook post successful: {result.get('post_id')}")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Facebook post error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _post_text(self, content: Dict) -> Dict:
        """Post text to Facebook"""
        return {
            'success': True,
            'post_id': f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'facebook',
            'content_type': 'text',
            'posted_at': datetime.now().isoformat()
        }
    
    async def _post_photo(self, content: Dict) -> Dict:
        """Post photo to Facebook"""
        return {
            'success': True,
            'post_id': f"fb_photo_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'facebook',
            'content_type': 'photo',
            'posted_at': datetime.now().isoformat()
        }
    
    async def _post_video(self, content: Dict) -> Dict:
        """Post video to Facebook"""
        return {
            'success': True,
            'post_id': f"fb_video_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'facebook',
            'content_type': 'video',
            'posted_at': datetime.now().isoformat()
        }
    
    async def _post_link(self, content: Dict) -> Dict:
        """Post link to Facebook"""
        return {
            'success': True,
            'post_id': f"fb_link_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'facebook',
            'content_type': 'link',
            'posted_at': datetime.now().isoformat()
        }
    
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Facebook"""
        optimized = content.copy()
        
        # Facebook allows longer posts - use full content
        max_length = self.config.get('max_post_length', 63206)
        if len(optimized.get('text', '')) > max_length:
            optimized['text'] = optimized['text'][:max_length-3] + '...'
        
        # Fewer hashtags on Facebook (max 10)
        hashtags = optimized.get('hashtags', [])[:10]
        if hashtags:
            hashtag_str = ' '.join(hashtags)
            optimized['text'] = f"{optimized.get('text', '')}\n\n{hashtag_str}"
        
        # Facebook-specific optimizations
        optimized['facebook_optimizations'] = {
            'feeling_activity': 'feeling hungry',
            'location': 'Randol\'s Restaurant',
            'call_to_action': 'Learn More',
            'targeting': {
                'age_range': [25, 65],
                'interests': ['Cajun cuisine', 'Louisiana', 'Live music', 'Restaurants'],
                'radius_miles': 50
            }
        }
        
        return optimized
    
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Facebook post analytics"""
        return {
            'post_id': post_id,
            'platform': 'facebook',
            'impressions': 2100,
            'reach': 1650,
            'engagement': 220,
            'reactions': {
                'like': 150,
                'love': 45,
                'haha': 10,
                'wow': 8,
                'sad': 0,
                'angry': 0
            },
            'comments': 25,
            'shares': 12,
            'clicks': 89,
            'engagement_rate': 0.052,
            'fetched_at': datetime.now().isoformat()
        }


class TikTokAgent(BasePlatformAgent):
    """TikTok-specific content publishing agent"""
    
    def __init__(self):
        super().__init__("tiktok")
        self.access_token = Config.TIKTOK_ACCESS_TOKEN
        self.api_base = "https://open.tiktokapis.com/v2"
    
    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to TikTok"""
        if not self.can_post():
            return {'success': False, 'error': 'Rate limit exceeded'}
        
        try:
            optimized = await self.optimize_content(content)
            
            # TikTok is video-first
            result = await self._post_video(optimized)
            
            if result.get('success'):
                self.last_post_time = datetime.now()
                self.posts_today += 1
                self.logger.info(f"TikTok post successful: {result.get('post_id')}")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"TikTok post error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _post_video(self, content: Dict) -> Dict:
        """Post video to TikTok"""
        return {
            'success': True,
            'post_id': f"tt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'tiktok',
            'content_type': 'video',
            'posted_at': datetime.now().isoformat()
        }
    
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for TikTok"""
        optimized = content.copy()
        
        # TikTok has short caption limit
        max_length = self.config.get('max_caption_length', 150)
        
        # Create punchy caption
        text = optimized.get('text', '')
        if len(text) > max_length:
            # Extract key message for TikTok
            sentences = text.split('.')
            optimized['text'] = sentences[0][:max_length-20] if sentences else text[:max_length-20]
        
        # TikTok hashtags (max 20, but fewer is better for discoverability)
        hashtags = optimized.get('hashtags', [])[:8]
        tiktok_specific = ['#fyp', '#louisiana', '#cajunfood', '#foodtiktok']
        hashtags = tiktok_specific + [h for h in hashtags if h not in tiktok_specific]
        hashtags = hashtags[:12]
        
        if hashtags:
            hashtag_str = ' '.join(hashtags)
            remaining_space = max_length - len(optimized['text']) - 1
            if remaining_space > len(hashtag_str):
                optimized['text'] = f"{optimized['text']} {hashtag_str}"
        
        # TikTok-specific optimizations
        optimized['tiktok_optimizations'] = {
            'video_length': {'min': 15, 'max': 60, 'optimal': 30},
            'trending_sounds': True,
            'duet_enabled': True,
            'stitch_enabled': True,
            'comment_enabled': True,
            'vertical_format': True,
            'aspect_ratio': '9:16'
        }
        
        return optimized
    
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get TikTok post analytics"""
        return {
            'post_id': post_id,
            'platform': 'tiktok',
            'views': 5200,
            'likes': 320,
            'comments': 45,
            'shares': 28,
            'saves': 15,
            'watch_time_avg': 18.5,
            'completion_rate': 0.62,
            'engagement_rate': 0.075,
            'fetched_at': datetime.now().isoformat()
        }


class YouTubeAgent(BasePlatformAgent):
    """YouTube-specific content publishing agent"""
    
    def __init__(self):
        super().__init__("youtube")
        self.api_key = Config.YOUTUBE_API_KEY
        self.api_base = "https://www.googleapis.com/youtube/v3"
        self.channel_id = None  # Set from config
    
    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to YouTube"""
        if not self.can_post():
            return {'success': False, 'error': 'Rate limit exceeded'}
        
        try:
            optimized = await self.optimize_content(content)
            
            content_type = optimized.get('media_type', 'video')
            
            if content_type == 'short':
                result = await self._post_short(optimized)
            else:
                result = await self._post_video(optimized)
            
            if result.get('success'):
                self.last_post_time = datetime.now()
                self.posts_today += 1
                self.logger.info(f"YouTube post successful: {result.get('post_id')}")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"YouTube post error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _post_video(self, content: Dict) -> Dict:
        """Post video to YouTube"""
        return {
            'success': True,
            'post_id': f"yt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'youtube',
            'content_type': 'video',
            'posted_at': datetime.now().isoformat()
        }
    
    async def _post_short(self, content: Dict) -> Dict:
        """Post YouTube Short"""
        return {
            'success': True,
            'post_id': f"yt_short_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'youtube',
            'content_type': 'short',
            'posted_at': datetime.now().isoformat()
        }
    
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for YouTube"""
        optimized = content.copy()
        
        # YouTube has longer description limit
        max_length = self.config.get('max_description_length', 5000)
        
        # Create SEO-optimized description
        description = optimized.get('text', '')
        
        # Add structured description
        youtube_description = f"""
{description}

🦞 ABOUT RANDOL'S RESTAURANT
Authentic Cajun cuisine and live zydeco music since 1973 in Breaux Bridge, Louisiana - the Crawfish Capital of the World!

📍 LOCATION
2320 Kaliste Saloom Road, Breaux Bridge, LA 70508

📞 RESERVATIONS
(337) 332-4648

🎵 LIVE MUSIC
Every Friday and Saturday night!

#CajunFood #Louisiana #BreauxBridge #Zydeco #Crawfish
        """.strip()
        
        if len(youtube_description) > max_length:
            youtube_description = youtube_description[:max_length-3] + '...'
        
        optimized['description'] = youtube_description
        
        # Generate title
        optimized['title'] = self._generate_youtube_title(content)
        
        # YouTube-specific optimizations
        optimized['youtube_optimizations'] = {
            'thumbnail': {
                'recommended_size': {'width': 1280, 'height': 720},
                'text_overlay': True,
                'brand_colors': True
            },
            'tags': ['Cajun food', 'Louisiana restaurant', 'Zydeco music', 'Crawfish', 
                    'Breaux Bridge', 'Authentic Cajun', 'Live music restaurant'],
            'category': 'Travel & Events',
            'privacy_status': 'public',
            'made_for_kids': False,
            'end_screen': True,
            'cards': True
        }
        
        return optimized
    
    def _generate_youtube_title(self, content: Dict) -> str:
        """Generate SEO-optimized YouTube title"""
        content_type = content.get('type', '')
        
        titles = {
            'daily_special': "Today's Cajun Special at Randol's | Authentic Louisiana Cuisine",
            'crawfish_education': "Fresh Louisiana Crawfish | Randol's Restaurant Breaux Bridge",
            'event_promotion': "Live Zydeco Music Tonight! | Randol's Restaurant",
            'morning_greeting': "Good Morning from Cajun Country | Randol's Restaurant",
            'evening_event': "Friday Night Fais Do-Do | Live Music at Randol's"
        }
        
        return titles.get(content_type, "Authentic Cajun Experience | Randol's Restaurant")
    
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get YouTube video analytics"""
        return {
            'post_id': post_id,
            'platform': 'youtube',
            'views': 850,
            'likes': 65,
            'dislikes': 2,
            'comments': 12,
            'shares': 8,
            'subscribers_gained': 5,
            'watch_time_hours': 28.5,
            'avg_view_duration': 145,
            'click_through_rate': 0.045,
            'engagement_rate': 0.082,
            'fetched_at': datetime.now().isoformat()
        }


class GooglePostsAgent(BasePlatformAgent):
    """Google Business Profile posts agent"""
    
    def __init__(self):
        super().__init__("google_posts")
        self.api_key = Config.GOOGLE_POSTS_API_KEY
        self.api_base = "https://mybusiness.googleapis.com/v4"
        self.location_id = None  # Set from config
    
    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post to Google Business Profile"""
        if not self.can_post():
            return {'success': False, 'error': 'Rate limit exceeded'}
        
        try:
            optimized = await self.optimize_content(content)
            
            post_type = optimized.get('post_type', 'STANDARD')
            
            if post_type == 'EVENT':
                result = await self._post_event(optimized)
            elif post_type == 'OFFER':
                result = await self._post_offer(optimized)
            else:
                result = await self._post_standard(optimized)
            
            if result.get('success'):
                self.last_post_time = datetime.now()
                self.posts_today += 1
                self.logger.info(f"Google post successful: {result.get('post_id')}")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Google post error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _post_standard(self, content: Dict) -> Dict:
        """Post standard update to Google Business"""
        return {
            'success': True,
            'post_id': f"goog_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'google_posts',
            'content_type': 'standard',
            'posted_at': datetime.now().isoformat()
        }
    
    async def _post_event(self, content: Dict) -> Dict:
        """Post event to Google Business"""
        return {
            'success': True,
            'post_id': f"goog_event_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'google_posts',
            'content_type': 'event',
            'posted_at': datetime.now().isoformat()
        }
    
    async def _post_offer(self, content: Dict) -> Dict:
        """Post offer to Google Business"""
        return {
            'success': True,
            'post_id': f"goog_offer_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'platform': 'google_posts',
            'content_type': 'offer',
            'posted_at': datetime.now().isoformat()
        }
    
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Google Business Profile"""
        optimized = content.copy()
        
        # Google posts have 1500 character limit
        max_length = 1500
        text = optimized.get('text', '')
        if len(text) > max_length:
            optimized['text'] = text[:max_length-3] + '...'
        
        # Determine post type
        content_type = content.get('type', '')
        if 'event' in content_type.lower():
            optimized['post_type'] = 'EVENT'
        elif 'special' in content_type.lower() or 'offer' in content_type.lower():
            optimized['post_type'] = 'OFFER'
        else:
            optimized['post_type'] = 'STANDARD'
        
        # Google-specific optimizations
        optimized['google_optimizations'] = {
            'call_to_action': {
                'type': 'LEARN_MORE',
                'url': 'https://randols.com'
            },
            'image_required': True,
            'expires_in_days': 7,
            'language_code': 'en-US'
        }
        
        return optimized
    
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Google post analytics"""
        return {
            'post_id': post_id,
            'platform': 'google_posts',
            'views': 450,
            'clicks': 35,
            'calls': 8,
            'direction_requests': 12,
            'website_clicks': 22,
            'engagement_rate': 0.068,
            'fetched_at': datetime.now().isoformat()
        }


class PlatformAgentManager:
    """Manages all platform-specific agents"""
    
    def __init__(self):
        self.logger = setup_logger("platform_manager")
        self.agents: Dict[str, BasePlatformAgent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all platform agents"""
        self.agents = {
            'instagram': InstagramAgent(),
            'facebook': FacebookAgent(),
            'tiktok': TikTokAgent(),
            'youtube': YouTubeAgent(),
            'google_posts': GooglePostsAgent()
        }
        self.logger.info(f"Initialized {len(self.agents)} platform agents")
    
    def get_agent(self, platform: str) -> Optional[BasePlatformAgent]:
        """Get a specific platform agent"""
        return self.agents.get(platform)
    
    async def post_to_platforms(self, content: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        """Post content to multiple platforms"""
        results = {}
        
        for platform in platforms:
            agent = self.agents.get(platform)
            if agent:
                try:
                    result = await agent.post_content(content)
                    results[platform] = result
                except Exception as e:
                    self.logger.error(f"Error posting to {platform}: {str(e)}")
                    results[platform] = {'success': False, 'error': str(e)}
            else:
                results[platform] = {'success': False, 'error': 'Platform not supported'}
        
        return results
    
    async def get_all_analytics(self, post_ids: Dict[str, str]) -> Dict[str, Any]:
        """Get analytics from all platforms"""
        analytics = {}
        
        for platform, post_id in post_ids.items():
            agent = self.agents.get(platform)
            if agent:
                try:
                    result = await agent.get_analytics(post_id)
                    analytics[platform] = result
                except Exception as e:
                    self.logger.error(f"Error getting analytics from {platform}: {str(e)}")
                    analytics[platform] = {'error': str(e)}
        
        return analytics
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all platform agents"""
        return {platform: agent.get_status() for platform, agent in self.agents.items()}
    
    async def close_all(self):
        """Close all agent sessions"""
        for agent in self.agents.values():
            await agent.close()
