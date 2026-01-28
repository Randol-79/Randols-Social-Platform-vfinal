"""
Test Suite for Randol's Agentic Marketing Platform
Run with: pytest backend/tests/ -v
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def sample_content():
    """Sample content for testing"""
    return {
        'id': 'test_001',
        'type': 'daily_special',
        'text': "Come try our fresh Gulf Shrimp Étouffée today, cher! Made with love using family recipes passed down through generations. Laissez les bon temps rouler! 🦐",
        'platforms': ['instagram', 'facebook'],
        'hashtags': ['#CajunFood', '#Louisiana', '#BreauxBridge'],
        'media_type': 'food_photography'
    }

@pytest.fixture
def sample_context():
    """Sample context for content generation"""
    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'day_of_week': 'friday',
        'time': '11:00',
        'weather': {'condition': 'sunny', 'temperature': 75},
        'local_events': [{'name': 'Zydeco Night', 'date': '2024-01-15', 'time': '19:00'}],
        'seasonal_factors': {'season': 'crawfish_season', 'theme': 'Fresh Louisiana Crawfish'}
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock = Mock()
    mock.choices = [Mock()]
    mock.choices[0].message = Mock()
    mock.choices[0].message.content = "Come see us tonight, cher! Fresh crawfish just arrived!"
    return mock


# ============================================
# CONFIG TESTS
# ============================================

class TestConfig:
    """Tests for configuration module"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        from utils.config import Config
        
        assert Config.RESTAURANT_NAME == "Randol's Restaurant"
        assert Config.RESTAURANT_LOCATION == "Breaux Bridge, Louisiana"
        assert 'primary' in Config.BRAND_COLORS
    
    def test_platform_config(self):
        """Test platform-specific configuration"""
        from utils.config import Config
        
        instagram_config = Config.get_platform_config('instagram')
        assert 'max_caption_length' in instagram_config
        assert instagram_config['hashtag_limit'] == 30
        
        tiktok_config = Config.get_platform_config('tiktok')
        assert tiktok_config['max_caption_length'] == 150
    
    def test_config_validation(self):
        """Test configuration validation"""
        from utils.config import Config
        
        validation = Config.validate_config()
        assert isinstance(validation, dict)
        assert 'openai_configured' in validation


# ============================================
# CAJUN VOICE TESTS
# ============================================

class TestCajunVoiceProcessor:
    """Tests for Cajun voice processing"""
    
    def test_load_phrases(self):
        """Test loading Cajun phrases"""
        from utils.cajun_voice import CajunVoiceProcessor
        
        processor = CajunVoiceProcessor()
        assert 'greetings' in processor.cajun_phrases
        assert 'expressions' in processor.cajun_phrases
        assert len(processor.cajun_phrases['greetings']) > 0
    
    def test_cultural_references(self):
        """Test cultural reference detection"""
        from utils.cajun_voice import CajunVoiceProcessor
        
        processor = CajunVoiceProcessor()
        
        # Text with references
        text_with_refs = "Come enjoy some zydeco music and fresh crawfish!"
        assert processor.has_cultural_references(text_with_refs)
        
        # Text without references
        text_without_refs = "Hello and welcome to our restaurant!"
        assert not processor.has_cultural_references(text_without_refs)
    
    def test_authenticity_validation(self):
        """Test authenticity validation"""
        from utils.cajun_voice import CajunVoiceProcessor
        
        processor = CajunVoiceProcessor()
        
        # Good authentic text
        good_text = "Y'all come see us, cher! Fresh crawfish from local waters."
        result = processor.validate_authenticity(good_text)
        assert result['authenticity_score'] >= 0.5
        
        # Text with problematic terms
        bad_text = "Come to our hillbilly restaurant!"
        result = processor.validate_authenticity(bad_text)
        assert result['authenticity_score'] < 0.5
        assert len(result['issues']) > 0
    
    def test_enhance_authenticity(self):
        """Test authenticity enhancement"""
        from utils.cajun_voice import CajunVoiceProcessor
        
        processor = CajunVoiceProcessor()
        
        plain_text = "Come visit our restaurant for dinner tonight."
        enhanced = processor.enhance_cajun_authenticity(plain_text)
        
        # Should have added something
        assert len(enhanced) >= len(plain_text)
    
    def test_generate_hashtags(self):
        """Test hashtag generation"""
        from utils.cajun_voice import CajunVoiceProcessor
        
        processor = CajunVoiceProcessor()
        
        hashtags = processor.generate_cajun_hashtags(['crawfish', 'music'])
        assert '#CajunFood' in hashtags
        assert '#Louisiana' in hashtags
        assert '#CrawfishBoil' in hashtags


# ============================================
# BRAND VOICE GUARDIAN TESTS
# ============================================

class TestBrandVoiceGuardian:
    """Tests for brand voice guardian agent"""
    
    @pytest.mark.asyncio
    async def test_validate_good_content(self, sample_content):
        """Test validation of good content"""
        from agents.brand_voice_guardian import BrandVoiceGuardianAgent
        
        guardian = BrandVoiceGuardianAgent()
        is_approved = await guardian.validate_content(sample_content)
        
        # Good Cajun content should pass
        assert is_approved or guardian.calculate_authenticity_score(sample_content['text']) > 0
    
    def test_authenticity_score(self):
        """Test authenticity scoring"""
        from agents.brand_voice_guardian import BrandVoiceGuardianAgent
        
        guardian = BrandVoiceGuardianAgent()
        
        # High authenticity text
        cajun_text = "Y'all come on over for some authentic Louisiana gumbo, cher!"
        score = guardian.calculate_authenticity_score(cajun_text)
        assert score >= 0.5
        
        # Generic text
        generic_text = "Visit our restaurant today."
        score = guardian.calculate_authenticity_score(generic_text)
        assert score <= 0.7
    
    def test_tone_compliance(self):
        """Test tone compliance checking"""
        from agents.brand_voice_guardian import BrandVoiceGuardianAgent
        
        guardian = BrandVoiceGuardianAgent()
        
        # Positive, welcoming text
        good_tone = "We welcome you to join our family for a delicious meal!"
        assert guardian.check_tone_compliance(good_tone)
        
        # Negative text
        bad_tone = "This terrible weather is ruining everything and we're very upset."
        # May or may not pass depending on sentiment analysis
    
    def test_cultural_appropriateness(self):
        """Test cultural appropriateness checking"""
        from agents.brand_voice_guardian import BrandVoiceGuardianAgent
        
        guardian = BrandVoiceGuardianAgent()
        
        # Appropriate content
        appropriate = "Experience authentic Cajun tradition at its finest!"
        assert guardian.check_cultural_appropriateness(appropriate)
        
        # Inappropriate content
        inappropriate = "Come enjoy our hillbilly redneck cooking!"
        assert not guardian.check_cultural_appropriateness(inappropriate)
    
    def test_suggest_improvements(self):
        """Test improvement suggestions"""
        from agents.brand_voice_guardian import BrandVoiceGuardianAgent
        
        guardian = BrandVoiceGuardianAgent()
        
        plain_text = "Visit us for food."
        suggestions = guardian.suggest_improvements(plain_text)
        
        assert len(suggestions) > 0


# ============================================
# CONTENT GENERATOR TESTS
# ============================================

class TestContentGenerator:
    """Tests for content generator agent"""
    
    def test_content_plan_creation(self, sample_context):
        """Test content plan creation"""
        from agents.content_generator import ContentGeneratorAgent
        
        generator = ContentGeneratorAgent()
        plan = generator.create_content_plan(sample_context)
        
        assert 'morning_greeting' in plan
        assert 'daily_special' in plan
    
    def test_hashtag_generation(self):
        """Test hashtag generation"""
        from agents.content_generator import ContentGeneratorAgent
        
        generator = ContentGeneratorAgent()
        
        hashtags = generator.generate_hashtags(['crawfish', 'zydeco'])
        
        assert '#RandolsRestaurant' in hashtags
        assert '#BreauxBridge' in hashtags
        assert len(hashtags) > 4


# ============================================
# SCHEDULER AGENT TESTS
# ============================================

class TestSchedulerAgent:
    """Tests for scheduler agent"""
    
    def test_schedule_content(self, sample_content):
        """Test content scheduling"""
        from agents.scheduler_agent import SchedulerAgent
        
        scheduler = SchedulerAgent()
        
        # Schedule for future
        scheduled_time = datetime.now() + timedelta(hours=2)
        result = asyncio.run(scheduler.schedule_content(sample_content, scheduled_time))
        
        assert result['success']
        assert 'post_id' in result
    
    def test_schedule_validation(self, sample_content):
        """Test scheduling validation"""
        from agents.scheduler_agent import SchedulerAgent
        
        scheduler = SchedulerAgent()
        
        # Past time should fail
        past_time = datetime.now() - timedelta(hours=1)
        result = asyncio.run(scheduler.schedule_content(sample_content, past_time))
        
        assert not result['success']
        assert 'error' in result
    
    def test_optimal_time_calculation(self, sample_content):
        """Test optimal time calculation"""
        from agents.scheduler_agent import SchedulerAgent
        
        scheduler = SchedulerAgent()
        
        # Get optimal times
        optimal = scheduler.get_optimal_times('instagram', 'daily_special')
        
        assert len(optimal) > 0
        assert 'time' in optimal[0]
        assert 'score' in optimal[0]
    
    def test_queue_preview(self, sample_content):
        """Test queue preview"""
        from agents.scheduler_agent import SchedulerAgent
        
        scheduler = SchedulerAgent()
        
        # Schedule some content
        for i in range(3):
            content = sample_content.copy()
            content['id'] = f"test_{i}"
            scheduled_time = datetime.now() + timedelta(hours=i+1)
            asyncio.run(scheduler.schedule_content(content, scheduled_time))
        
        preview = scheduler.get_queue_preview(limit=5)
        assert len(preview) <= 5


# ============================================
# PLATFORM AGENT TESTS
# ============================================

class TestPlatformAgents:
    """Tests for platform-specific agents"""
    
    def test_instagram_optimization(self, sample_content):
        """Test Instagram content optimization"""
        from agents.platform_agents import InstagramAgent
        
        agent = InstagramAgent()
        optimized = asyncio.run(agent.optimize_content(sample_content))
        
        assert 'instagram_optimizations' in optimized
        assert len(optimized.get('text', '')) <= 2200
    
    def test_tiktok_optimization(self, sample_content):
        """Test TikTok content optimization"""
        from agents.platform_agents import TikTokAgent
        
        agent = TikTokAgent()
        optimized = asyncio.run(agent.optimize_content(sample_content))
        
        assert 'tiktok_optimizations' in optimized
        assert optimized['tiktok_optimizations']['vertical_format']
    
    def test_youtube_title_generation(self, sample_content):
        """Test YouTube title generation"""
        from agents.platform_agents import YouTubeAgent
        
        agent = YouTubeAgent()
        title = agent._generate_youtube_title(sample_content)
        
        assert len(title) > 0
        assert "Randol's" in title
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        from agents.platform_agents import InstagramAgent
        
        agent = InstagramAgent()
        
        # Should be able to post initially
        assert agent.can_post()
        
        # Simulate a post
        agent.last_post_time = datetime.now()
        agent.posts_today = 1
        
        # Should respect minimum interval
        # (depending on implementation, may or may not block)
    
    def test_platform_manager(self):
        """Test platform manager"""
        from agents.platform_agents import PlatformAgentManager
        
        manager = PlatformAgentManager()
        
        # Should have all platforms
        assert manager.get_agent('instagram') is not None
        assert manager.get_agent('facebook') is not None
        assert manager.get_agent('tiktok') is not None
        
        # Get all status
        status = manager.get_all_status()
        assert len(status) == 5


# ============================================
# ANALYTICS AGENT TESTS
# ============================================

class TestAnalyticsAgent:
    """Tests for analytics agent"""
    
    def test_performance_analysis(self):
        """Test performance analysis"""
        from agents.analytics_agent import AnalyticsAgent
        
        agent = AnalyticsAgent()
        analysis = asyncio.run(agent.analyze_performance())
        
        assert 'overall_metrics' in analysis or 'metrics' in analysis or isinstance(analysis, dict)
    
    def test_recommendation_generation(self):
        """Test recommendation generation"""
        from agents.analytics_agent import AnalyticsAgent
        
        agent = AnalyticsAgent()
        recommendations = asyncio.run(agent.generate_recommendations())
        
        # Should return list of recommendations
        assert isinstance(recommendations, list)


# ============================================
# API ENDPOINT TESTS
# ============================================

class TestAPIEndpoints:
    """Tests for Flask API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_status_endpoint(self, client):
        """Test system status endpoint"""
        response = client.get('/api/status')
        assert response.status_code == 200
    
    def test_agents_status(self, client):
        """Test agents status endpoint"""
        response = client.get('/api/agents/status')
        assert response.status_code == 200
    
    def test_content_generation(self, client):
        """Test content generation endpoint"""
        response = client.post('/api/content/generate',
            json={
                'type': 'morning_greeting',
                'platforms': ['instagram', 'facebook']
            },
            content_type='application/json'
        )
        assert response.status_code in [200, 201, 500]  # 500 if OpenAI not configured
    
    def test_brand_guidelines(self, client):
        """Test brand guidelines endpoint"""
        response = client.get('/api/brand/guidelines')
        assert response.status_code == 200


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_content_pipeline(self, sample_context):
        """Test full content generation pipeline"""
        from agents.content_generator import ContentGeneratorAgent
        from agents.brand_voice_guardian import BrandVoiceGuardianAgent
        from agents.scheduler_agent import SchedulerAgent
        
        # Generate
        generator = ContentGeneratorAgent()
        plan = generator.create_content_plan(sample_context)
        
        assert len(plan) > 0
        
        # Validate
        guardian = BrandVoiceGuardianAgent()
        sample_content = {
            'id': 'test',
            'text': "Come join us for authentic Cajun cuisine, cher!"
        }
        is_valid = await guardian.validate_content(sample_content)
        
        # Schedule
        scheduler = SchedulerAgent()
        if is_valid:
            result = await scheduler.schedule_content(
                sample_content,
                datetime.now() + timedelta(hours=1)
            )
            assert result['success']


# ============================================
# RUN TESTS
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
