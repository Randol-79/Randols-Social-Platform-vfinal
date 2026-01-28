"""
Pytest Configuration for Randol's Agentic Marketing Platform
"""

import pytest
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing"""
    from api.app import app
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    return app


@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_openai():
    """Mock OpenAI client"""
    from unittest.mock import Mock, AsyncMock
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Test Cajun content, cher!"
    
    mock_client = Mock()
    mock_client.chat.completions.acreate = AsyncMock(return_value=mock_response)
    
    return mock_client


@pytest.fixture
def sample_post_data():
    """Sample post data for testing"""
    return {
        'id': 'test_post_001',
        'type': 'daily_special',
        'text': "Try our fresh Gulf Shrimp Étouffée today! Made with love, cher.",
        'platforms': ['instagram', 'facebook'],
        'hashtags': ['#CajunFood', '#Louisiana', '#BreauxBridge'],
        'scheduled_time': '2024-01-15T12:00:00',
        'status': 'scheduled'
    }


@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing"""
    return {
        'instagram': {
            'impressions': 1500,
            'reach': 1200,
            'engagement': 180,
            'likes': 150,
            'comments': 20,
            'saves': 10
        },
        'facebook': {
            'impressions': 2000,
            'reach': 1600,
            'engagement': 220,
            'reactions': 180,
            'comments': 25,
            'shares': 15
        }
    }


# Environment setup for tests
def pytest_configure(config):
    """Configure test environment"""
    os.environ.setdefault('FLASK_ENV', 'testing')
    os.environ.setdefault('MOCK_SOCIAL_POSTS', 'true')
    os.environ.setdefault('DEMO_MODE', 'true')


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Mark async tests
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
