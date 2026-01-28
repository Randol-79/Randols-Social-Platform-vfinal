"""
API Routes for Randol's Agentic Marketing Platform
Complete REST API with WebSocket support
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta
import asyncio
import json
from typing import Dict, Any, Optional

from utils.logger import setup_logger
from utils.config import Config

logger = setup_logger("api_routes")


# ========================
# Blueprint Definitions
# ========================

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
content_bp = Blueprint('content', __name__, url_prefix='/api/v1/content')
schedule_bp = Blueprint('schedule', __name__, url_prefix='/api/v1/schedule')
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/v1/analytics')
agents_bp = Blueprint('agents', __name__, url_prefix='/api/v1/agents')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')


# ========================
# Decorators
# ========================

def async_route(f):
    """Decorator to run async functions in Flask routes"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


def validate_json(*required_fields):
    """Decorator to validate required JSON fields"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            missing = [field for field in required_fields if field not in data]
            
            if missing:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing
                }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def handle_errors(f):
    """Decorator to handle exceptions gracefully"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    return wrapper


# ========================
# Core API Routes
# ========================

@api_bp.route('/health', methods=['GET'])
@handle_errors
def health_check():
    """System health check endpoint"""
    from database import db_manager
    
    db_health = db_manager.check_health()
    
    return jsonify({
        'status': 'healthy' if db_health['connected'] else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': {
            'api': 'healthy',
            'database': db_health['status'],
            'redis': _check_redis_health()
        }
    })


def _check_redis_health() -> str:
    """Check Redis connection health"""
    try:
        import redis
        r = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD or None
        )
        r.ping()
        return 'healthy'
    except:
        return 'unavailable'


@api_bp.route('/status', methods=['GET'])
@handle_errors
@async_route
async def system_status():
    """Get comprehensive system status"""
    from agents.master_orchestrator import MasterOrchestratorAgent
    
    orchestrator = MasterOrchestratorAgent()
    status = orchestrator.get_system_status()
    
    return jsonify(status)


@api_bp.route('/config', methods=['GET'])
@handle_errors
def get_config():
    """Get public configuration"""
    return jsonify({
        'restaurant': {
            'name': Config.RESTAURANT_NAME,
            'location': Config.RESTAURANT_LOCATION,
            'established': Config.RESTAURANT_ESTABLISHED
        },
        'brand_colors': Config.BRAND_COLORS,
        'posting_schedule': Config.POSTING_SCHEDULE,
        'content_limits': Config.CONTENT_LIMITS,
        'platforms': ['instagram', 'facebook', 'tiktok', 'youtube', 'google_posts']
    })


# ========================
# Content Routes
# ========================

@content_bp.route('/', methods=['GET'])
@handle_errors
@async_route
async def list_content():
    """List content with filtering and pagination"""
    from database import ContentRepository, ContentStatus
    
    # Query parameters
    status = request.args.get('status')
    content_type = request.args.get('type')
    platform = request.args.get('platform')
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    
    repo = ContentRepository()
    
    if status:
        content = await repo.get_by_status(ContentStatus(status), limit=limit)
    else:
        content = await repo.get_recent(days=30, limit=limit)
    
    return jsonify({
        'content': content,
        'pagination': {
            'limit': limit,
            'offset': offset,
            'total': len(content)
        }
    })


@content_bp.route('/<content_id>', methods=['GET'])
@handle_errors
@async_route
async def get_content(content_id: str):
    """Get content by ID"""
    from database import ContentRepository
    
    repo = ContentRepository()
    content = await repo.get_by_id(content_id)
    
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    return jsonify(content)


@content_bp.route('/', methods=['POST'])
@handle_errors
@validate_json('text', 'content_type', 'platforms')
@async_route
async def create_content():
    """Create new content"""
    from database import ContentRepository, ContentStatus
    from agents.brand_voice_guardian import BrandVoiceGuardianAgent
    
    data = request.get_json()
    
    # Create content document
    content = {
        'text': data['text'],
        'content_type': data['content_type'],
        'platforms': data['platforms'],
        'hashtags': data.get('hashtags', []),
        'media': data.get('media', []),
        'context': data.get('context', {}),
        'status': ContentStatus.DRAFT.value,
        'created_by': data.get('created_by', 'api')
    }
    
    # Auto-validate if requested
    if data.get('auto_validate', True):
        guardian = BrandVoiceGuardianAgent()
        is_valid = await guardian.validate_content({'text': content['text']})
        
        if is_valid:
            content['status'] = ContentStatus.APPROVED.value
            content['validation'] = {
                'authenticity_score': guardian.calculate_authenticity_score(content['text']),
                'validated_at': datetime.utcnow().isoformat(),
                'validated_by': 'brand_voice_guardian'
            }
        else:
            content['status'] = ContentStatus.PENDING_REVIEW.value
            content['validation'] = {
                'issues': guardian.suggest_improvements(content['text'])
            }
    
    repo = ContentRepository()
    content_id = await repo.create(content)
    
    return jsonify({
        'id': content_id,
        'status': content['status'],
        'message': 'Content created successfully'
    }), 201


@content_bp.route('/<content_id>', methods=['PUT'])
@handle_errors
@async_route
async def update_content(content_id: str):
    """Update content"""
    from database import ContentRepository
    
    data = request.get_json()
    
    # Remove fields that shouldn't be updated directly
    protected_fields = ['_id', 'id', 'created_at', 'created_by']
    updates = {k: v for k, v in data.items() if k not in protected_fields}
    
    repo = ContentRepository()
    success = await repo.update(content_id, updates)
    
    if not success:
        return jsonify({'error': 'Content not found or not modified'}), 404
    
    return jsonify({'message': 'Content updated successfully'})


@content_bp.route('/<content_id>', methods=['DELETE'])
@handle_errors
@async_route
async def delete_content(content_id: str):
    """Delete (archive) content"""
    from database import ContentRepository
    
    repo = ContentRepository()
    success = await repo.delete(content_id)
    
    if not success:
        return jsonify({'error': 'Content not found'}), 404
    
    return jsonify({'message': 'Content archived successfully'})


@content_bp.route('/generate', methods=['POST'])
@handle_errors
@validate_json('content_type')
@async_route
async def generate_content():
    """Generate new content using AI"""
    from agents.content_generator import ContentGeneratorAgent
    from agents.master_orchestrator import MasterOrchestratorAgent
    
    data = request.get_json()
    content_type = data['content_type']
    
    # Get context
    orchestrator = MasterOrchestratorAgent()
    context = await orchestrator.gather_context()
    context.update(data.get('context', {}))
    
    # Generate content
    generator = ContentGeneratorAgent()
    content = await generator.generate_content_by_type(content_type, context)
    
    if not content:
        return jsonify({'error': f'Could not generate {content_type} content'}), 400
    
    return jsonify(content)


@content_bp.route('/validate', methods=['POST'])
@handle_errors
@validate_json('text')
@async_route
async def validate_content():
    """Validate content against brand guidelines"""
    from agents.brand_voice_guardian import BrandVoiceGuardianAgent
    
    data = request.get_json()
    
    guardian = BrandVoiceGuardianAgent()
    is_valid = await guardian.validate_content({'text': data['text']})
    authenticity_score = guardian.calculate_authenticity_score(data['text'])
    suggestions = guardian.suggest_improvements(data['text'])
    
    return jsonify({
        'valid': is_valid,
        'authenticity_score': authenticity_score,
        'suggestions': suggestions,
        'tone_compliance': guardian.check_tone_compliance(data['text']),
        'cultural_appropriateness': guardian.check_cultural_appropriateness(data['text']),
        'brand_consistency': guardian.check_brand_consistency(data['text'])
    })


@content_bp.route('/enhance', methods=['POST'])
@handle_errors
@validate_json('text')
@async_route
async def enhance_content():
    """Enhance content with Cajun authenticity"""
    from utils.cajun_voice import CajunVoiceProcessor
    
    data = request.get_json()
    
    processor = CajunVoiceProcessor()
    enhanced_text = processor.enhance_cajun_authenticity(data['text'])
    validation = processor.validate_authenticity(enhanced_text)
    hashtags = processor.generate_cajun_hashtags(data.get('keywords', []))
    
    return jsonify({
        'original': data['text'],
        'enhanced': enhanced_text,
        'validation': validation,
        'suggested_hashtags': hashtags
    })


# ========================
# Schedule Routes
# ========================

@schedule_bp.route('/', methods=['GET'])
@handle_errors
@async_route
async def get_schedule():
    """Get scheduled posts"""
    from database import ScheduleRepository
    
    date = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    
    repo = ScheduleRepository()
    posts = await repo.get_for_date(date)
    
    return jsonify({
        'date': date,
        'posts': posts,
        'total': len(posts)
    })


@schedule_bp.route('/pending', methods=['GET'])
@handle_errors
@async_route
async def get_pending_posts():
    """Get posts pending publication"""
    from database import ScheduleRepository
    
    repo = ScheduleRepository()
    posts = await repo.get_pending()
    
    return jsonify({
        'pending_posts': posts,
        'total': len(posts)
    })


@schedule_bp.route('/', methods=['POST'])
@handle_errors
@validate_json('content_id', 'platform', 'scheduled_time')
@async_route
async def schedule_post():
    """Schedule content for posting"""
    from database import ScheduleRepository, ContentRepository
    from agents.scheduler_agent import SchedulerAgent
    
    data = request.get_json()
    
    # Verify content exists
    content_repo = ContentRepository()
    content = await content_repo.get_by_id(data['content_id'])
    
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    # Parse scheduled time
    scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
    
    # Create scheduled post
    post = {
        'content_id': data['content_id'],
        'platform': data['platform'],
        'scheduled_time': scheduled_time,
        'priority': data.get('priority', 'normal'),
        'status': 'pending'
    }
    
    schedule_repo = ScheduleRepository()
    post_id = await schedule_repo.create(post)
    
    return jsonify({
        'id': post_id,
        'message': 'Post scheduled successfully',
        'scheduled_time': scheduled_time.isoformat()
    }), 201


@schedule_bp.route('/<post_id>/cancel', methods=['POST'])
@handle_errors
@async_route
async def cancel_scheduled_post(post_id: str):
    """Cancel a scheduled post"""
    from database import ScheduleRepository
    
    repo = ScheduleRepository()
    success = await repo.cancel_post(post_id)
    
    if not success:
        return jsonify({'error': 'Post not found'}), 404
    
    return jsonify({'message': 'Post cancelled successfully'})


@schedule_bp.route('/calendar', methods=['GET'])
@handle_errors
@async_route
async def get_calendar():
    """Get content calendar view"""
    from database import ScheduleRepository
    
    start_date = request.args.get('start', datetime.utcnow().strftime('%Y-%m-%d'))
    days = int(request.args.get('days', 7))
    
    repo = ScheduleRepository()
    calendar = {}
    
    for i in range(days):
        date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=i)).strftime('%Y-%m-%d')
        posts = await repo.get_for_date(date)
        calendar[date] = {
            'posts': posts,
            'total': len(posts),
            'by_platform': {}
        }
        
        # Group by platform
        for post in posts:
            platform = post.get('platform', 'unknown')
            if platform not in calendar[date]['by_platform']:
                calendar[date]['by_platform'][platform] = 0
            calendar[date]['by_platform'][platform] += 1
    
    return jsonify(calendar)


@schedule_bp.route('/optimal-times', methods=['GET'])
@handle_errors
@async_route
async def get_optimal_times():
    """Get optimal posting times"""
    from agents.feedback_loop_agent import FeedbackLoopAgent
    
    agent = FeedbackLoopAgent()
    optimal_times = await agent.get_optimal_posting_times()
    
    return jsonify(optimal_times)


# ========================
# Analytics Routes
# ========================

@analytics_bp.route('/daily', methods=['GET'])
@handle_errors
@async_route
async def get_daily_analytics():
    """Get daily analytics"""
    from database import AnalyticsRepository
    
    date = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    
    repo = AnalyticsRepository()
    analytics = await repo.get_daily(date)
    
    if not analytics:
        return jsonify({'error': 'No analytics for this date'}), 404
    
    return jsonify(analytics)


@analytics_bp.route('/range', methods=['GET'])
@handle_errors
@async_route
async def get_analytics_range():
    """Get analytics for date range"""
    from database import AnalyticsRepository
    
    end_date = request.args.get('end', datetime.utcnow().strftime('%Y-%m-%d'))
    start_date = request.args.get('start', (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'))
    
    repo = AnalyticsRepository()
    analytics = await repo.get_daily_range(start_date, end_date)
    
    return jsonify({
        'start_date': start_date,
        'end_date': end_date,
        'days': len(analytics),
        'analytics': analytics
    })


@analytics_bp.route('/weekly', methods=['GET'])
@handle_errors
@async_route
async def get_weekly_reports():
    """Get weekly reports"""
    from database import AnalyticsRepository
    
    limit = int(request.args.get('limit', 12))
    
    repo = AnalyticsRepository()
    reports = await repo.get_weekly_reports(limit)
    
    return jsonify({
        'reports': reports,
        'total': len(reports)
    })


@analytics_bp.route('/platform/<platform>', methods=['GET'])
@handle_errors
@async_route
async def get_platform_analytics(platform: str):
    """Get platform-specific analytics"""
    from database import AnalyticsRepository
    
    days = int(request.args.get('days', 30))
    
    repo = AnalyticsRepository()
    summary = await repo.get_platform_summary(platform, days)
    
    return jsonify({
        'platform': platform,
        'period_days': days,
        'summary': summary
    })


@analytics_bp.route('/performance', methods=['GET'])
@handle_errors
@async_route
async def get_performance_analysis():
    """Get comprehensive performance analysis"""
    from agents.feedback_loop_agent import FeedbackLoopAgent
    
    period = request.args.get('period', '7d')
    
    agent = FeedbackLoopAgent()
    analysis = await agent.analyze_performance(period)
    
    return jsonify(analysis)


@analytics_bp.route('/recommendations', methods=['GET'])
@handle_errors
@async_route
async def get_recommendations():
    """Get AI-powered recommendations"""
    from agents.feedback_loop_agent import FeedbackLoopAgent
    from agents.analytics_agent import AnalyticsAgent
    
    feedback_agent = FeedbackLoopAgent()
    analytics_agent = AnalyticsAgent()
    
    # Get performance analysis
    analysis = await feedback_agent.analyze_performance('7d')
    recommendations = analysis.get('recommendations', [])
    
    # Get additional recommendations from analytics agent
    analytics_recommendations = await analytics_agent.get_recommendations()
    
    return jsonify({
        'recommendations': recommendations,
        'analytics_insights': analytics_recommendations,
        'generated_at': datetime.utcnow().isoformat()
    })


# ========================
# Agent Routes
# ========================

@agents_bp.route('/', methods=['GET'])
@handle_errors
@async_route
async def list_agents():
    """List all agents and their status"""
    from database import AgentRepository
    
    repo = AgentRepository()
    states = await repo.get_all_states()
    
    # Add default states for agents not in DB
    default_agents = [
        'master_orchestrator', 'content_generator', 'brand_voice_guardian',
        'analytics', 'feedback_loop', 'scheduler'
    ]
    
    agent_map = {s['agent_name']: s for s in states}
    
    agents = []
    for name in default_agents:
        if name in agent_map:
            agents.append(agent_map[name])
        else:
            agents.append({
                'agent_name': name,
                'status': 'active',
                'health': 'good'
            })
    
    return jsonify({
        'agents': agents,
        'total': len(agents)
    })


@agents_bp.route('/<agent_name>', methods=['GET'])
@handle_errors
@async_route
async def get_agent_status(agent_name: str):
    """Get specific agent status"""
    # Get agent instance and status
    agent = _get_agent_instance(agent_name)
    
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    
    status = agent.get_status() if hasattr(agent, 'get_status') else {'status': 'unknown'}
    
    return jsonify({
        'agent_name': agent_name,
        **status
    })


def _get_agent_instance(agent_name: str):
    """Get agent instance by name"""
    agents = {
        'master_orchestrator': 'agents.master_orchestrator.MasterOrchestratorAgent',
        'content_generator': 'agents.content_generator.ContentGeneratorAgent',
        'brand_voice_guardian': 'agents.brand_voice_guardian.BrandVoiceGuardianAgent',
        'analytics': 'agents.analytics_agent.AnalyticsAgent',
        'feedback_loop': 'agents.feedback_loop_agent.FeedbackLoopAgent',
        'scheduler': 'agents.scheduler_agent.SchedulerAgent'
    }
    
    if agent_name not in agents:
        return None
    
    module_path, class_name = agents[agent_name].rsplit('.', 1)
    
    try:
        import importlib
        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)
        return agent_class()
    except Exception as e:
        logger.error(f"Error instantiating agent {agent_name}: {e}")
        return None


@agents_bp.route('/<agent_name>/logs', methods=['GET'])
@handle_errors
@async_route
async def get_agent_logs(agent_name: str):
    """Get agent logs"""
    from database import AgentRepository
    
    limit = int(request.args.get('limit', 100))
    
    repo = AgentRepository()
    logs = await repo.get_logs(agent_name, limit)
    
    return jsonify({
        'agent_name': agent_name,
        'logs': logs,
        'total': len(logs)
    })


@agents_bp.route('/logs/errors', methods=['GET'])
@handle_errors
@async_route
async def get_error_logs():
    """Get recent error logs across all agents"""
    from database import AgentRepository
    
    hours = int(request.args.get('hours', 24))
    
    repo = AgentRepository()
    errors = await repo.get_error_logs(hours)
    
    return jsonify({
        'period_hours': hours,
        'errors': errors,
        'total': len(errors)
    })


# ========================
# Admin Routes
# ========================

@admin_bp.route('/emergency-override', methods=['POST'])
@handle_errors
@validate_json('reason')
@async_route
async def emergency_override():
    """Trigger emergency override"""
    from agents.master_orchestrator import MasterOrchestratorAgent
    
    data = request.get_json()
    
    orchestrator = MasterOrchestratorAgent()
    result = await orchestrator.handle_emergency_override({
        'reason': data['reason'],
        'message': data.get('message'),
        'platforms': data.get('platforms', ['facebook', 'instagram']),
        'generate_content': data.get('generate_content', False)
    })
    
    return jsonify(result)


@admin_bp.route('/pause', methods=['POST'])
@handle_errors
@async_route
async def pause_system():
    """Pause all agent activities"""
    from agents.master_orchestrator import MasterOrchestratorAgent
    
    orchestrator = MasterOrchestratorAgent()
    await orchestrator.pause_all_agents()
    
    return jsonify({
        'message': 'System paused',
        'status': orchestrator.get_system_status()
    })


@admin_bp.route('/resume', methods=['POST'])
@handle_errors
@async_route
async def resume_system():
    """Resume all agent activities"""
    from agents.master_orchestrator import MasterOrchestratorAgent
    
    orchestrator = MasterOrchestratorAgent()
    await orchestrator.resume_all_agents()
    
    return jsonify({
        'message': 'System resumed',
        'status': orchestrator.get_system_status()
    })


@admin_bp.route('/run-workflow', methods=['POST'])
@handle_errors
@async_route
async def run_workflow():
    """Manually trigger daily workflow"""
    from agents.master_orchestrator import MasterOrchestratorAgent
    
    orchestrator = MasterOrchestratorAgent()
    posts = await orchestrator.execute_daily_workflow()
    
    return jsonify({
        'message': 'Workflow executed',
        'posts_created': len(posts),
        'posts': posts
    })


@admin_bp.route('/ab-test', methods=['POST'])
@handle_errors
@validate_json('name', 'test_type', 'variable')
@async_route
async def start_ab_test():
    """Start an A/B test"""
    from agents.feedback_loop_agent import FeedbackLoopAgent
    
    data = request.get_json()
    
    agent = FeedbackLoopAgent()
    test_id = await agent.start_ab_test({
        'name': data['name'],
        'test_type': data['test_type'],
        'variable': data['variable'],
        'hypothesis': data.get('hypothesis'),
        'duration_days': data.get('duration_days', 7)
    })
    
    return jsonify({
        'test_id': test_id,
        'message': 'A/B test started'
    }), 201


@admin_bp.route('/ab-test/<test_id>/evaluate', methods=['POST'])
@handle_errors
@async_route
async def evaluate_ab_test(test_id: str):
    """Evaluate A/B test results"""
    from agents.feedback_loop_agent import FeedbackLoopAgent
    
    agent = FeedbackLoopAgent()
    results = await agent.evaluate_ab_test(test_id)
    
    return jsonify(results)


@admin_bp.route('/notifications', methods=['GET'])
@handle_errors
@async_route
async def get_notifications():
    """Get system notifications"""
    from database import NotificationRepository
    
    repo = NotificationRepository()
    notifications = await repo.get_unread()
    
    return jsonify({
        'notifications': notifications,
        'unread_count': len(notifications)
    })


@admin_bp.route('/notifications/<notification_id>/read', methods=['POST'])
@handle_errors
@async_route
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    from database import NotificationRepository
    
    repo = NotificationRepository()
    success = await repo.mark_read(notification_id)
    
    if not success:
        return jsonify({'error': 'Notification not found'}), 404
    
    return jsonify({'message': 'Notification marked as read'})


@admin_bp.route('/database/health', methods=['GET'])
@handle_errors
@async_route
async def database_health():
    """Check database health"""
    from database import db_manager
    
    health = await db_manager.check_health_async()
    
    return jsonify(health)


@admin_bp.route('/database/initialize', methods=['POST'])
@handle_errors
@async_route
async def initialize_database_route():
    """Initialize database indexes and setup"""
    from database import initialize_database
    
    await initialize_database()
    
    return jsonify({
        'message': 'Database initialized successfully'
    })


# ========================
# Brand Guidelines Routes
# ========================

@api_bp.route('/brand/guidelines', methods=['GET'])
@handle_errors
def get_brand_guidelines():
    """Get brand voice guidelines"""
    from agents.brand_voice_guardian import BrandVoiceGuardianAgent
    
    guardian = BrandVoiceGuardianAgent()
    
    return jsonify({
        'voice_guidelines': guardian.voice_guidelines,
        'approved_phrases': guardian.approved_phrases,
        'flagged_phrases': guardian.flagged_phrases,
        'authenticity_threshold': guardian.authenticity_threshold
    })


@api_bp.route('/brand/cajun-phrases', methods=['GET'])
@handle_errors
def get_cajun_phrases():
    """Get Cajun phrases and cultural references"""
    from utils.cajun_voice import CajunVoiceProcessor
    
    processor = CajunVoiceProcessor()
    
    return jsonify({
        'phrases': processor.cajun_phrases,
        'cultural_references': processor.cultural_references,
        'seasonal_terms': processor.seasonal_terms,
        'voice_patterns': processor.voice_patterns
    })


# ========================
# Register Blueprints Function
# ========================

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(api_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(admin_bp)
    
    logger.info("API blueprints registered")
