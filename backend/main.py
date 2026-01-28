"""
Main Flask Application Entry Point
Randol's Agentic Marketing Platform API Server
"""

import os
import sys
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config
from utils.logger import setup_logger
from api.routes import register_blueprints

# Initialize logger
logger = setup_logger("main_app")


def create_app(config_name: str = None) -> Flask:
    """
    Application factory for creating Flask app instances
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'randols-dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"]
        }
    })
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register before/after request handlers
    register_request_handlers(app)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Randol\'s Agentic Marketing Platform',
            'version': '1.0.0',
            'status': 'operational',
            'documentation': '/api/v1/docs',
            'health': '/api/v1/health',
            'restaurant': {
                'name': Config.RESTAURANT_NAME,
                'location': Config.RESTAURANT_LOCATION
            }
        })
    
    # API documentation endpoint
    @app.route('/api/v1/docs')
    def api_docs():
        return jsonify({
            'title': 'Randol\'s Marketing Platform API',
            'version': '1.0.0',
            'base_url': '/api/v1',
            'endpoints': {
                'health': {
                    'path': '/api/v1/health',
                    'method': 'GET',
                    'description': 'System health check'
                },
                'status': {
                    'path': '/api/v1/status',
                    'method': 'GET',
                    'description': 'Comprehensive system status'
                },
                'content': {
                    'list': {'path': '/api/v1/content', 'method': 'GET'},
                    'create': {'path': '/api/v1/content', 'method': 'POST'},
                    'get': {'path': '/api/v1/content/<id>', 'method': 'GET'},
                    'update': {'path': '/api/v1/content/<id>', 'method': 'PUT'},
                    'delete': {'path': '/api/v1/content/<id>', 'method': 'DELETE'},
                    'generate': {'path': '/api/v1/content/generate', 'method': 'POST'},
                    'validate': {'path': '/api/v1/content/validate', 'method': 'POST'},
                    'enhance': {'path': '/api/v1/content/enhance', 'method': 'POST'}
                },
                'schedule': {
                    'list': {'path': '/api/v1/schedule', 'method': 'GET'},
                    'create': {'path': '/api/v1/schedule', 'method': 'POST'},
                    'pending': {'path': '/api/v1/schedule/pending', 'method': 'GET'},
                    'calendar': {'path': '/api/v1/schedule/calendar', 'method': 'GET'},
                    'cancel': {'path': '/api/v1/schedule/<id>/cancel', 'method': 'POST'},
                    'optimal_times': {'path': '/api/v1/schedule/optimal-times', 'method': 'GET'}
                },
                'analytics': {
                    'daily': {'path': '/api/v1/analytics/daily', 'method': 'GET'},
                    'range': {'path': '/api/v1/analytics/range', 'method': 'GET'},
                    'weekly': {'path': '/api/v1/analytics/weekly', 'method': 'GET'},
                    'platform': {'path': '/api/v1/analytics/platform/<platform>', 'method': 'GET'},
                    'performance': {'path': '/api/v1/analytics/performance', 'method': 'GET'},
                    'recommendations': {'path': '/api/v1/analytics/recommendations', 'method': 'GET'}
                },
                'agents': {
                    'list': {'path': '/api/v1/agents', 'method': 'GET'},
                    'status': {'path': '/api/v1/agents/<name>', 'method': 'GET'},
                    'logs': {'path': '/api/v1/agents/<name>/logs', 'method': 'GET'},
                    'errors': {'path': '/api/v1/agents/logs/errors', 'method': 'GET'}
                },
                'admin': {
                    'emergency': {'path': '/api/v1/admin/emergency-override', 'method': 'POST'},
                    'pause': {'path': '/api/v1/admin/pause', 'method': 'POST'},
                    'resume': {'path': '/api/v1/admin/resume', 'method': 'POST'},
                    'workflow': {'path': '/api/v1/admin/run-workflow', 'method': 'POST'},
                    'ab_test': {'path': '/api/v1/admin/ab-test', 'method': 'POST'},
                    'notifications': {'path': '/api/v1/admin/notifications', 'method': 'GET'}
                },
                'brand': {
                    'guidelines': {'path': '/api/v1/brand/guidelines', 'method': 'GET'},
                    'cajun_phrases': {'path': '/api/v1/brand/cajun-phrases', 'method': 'GET'}
                }
            }
        })
    
    logger.info(f"Flask app created: {app.name}")
    return app


def register_error_handlers(app: Flask):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'Method {request.method} not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(429)
    def rate_limited(error):
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


def register_request_handlers(app: Flask):
    """Register before/after request handlers"""
    
    @app.before_request
    def before_request():
        """Log incoming requests"""
        request.start_time = datetime.utcnow()
        
        # Skip logging for health checks
        if request.path == '/api/v1/health':
            return
        
        logger.debug(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Add headers and log response"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add request ID if present
        request_id = request.headers.get('X-Request-ID')
        if request_id:
            response.headers['X-Request-ID'] = request_id
        
        # Log response time
        if hasattr(request, 'start_time') and request.path != '/api/v1/health':
            duration = (datetime.utcnow() - request.start_time).total_seconds() * 1000
            logger.debug(f"Response: {response.status_code} in {duration:.2f}ms")
        
        return response


# ========================
# WebSocket Support
# ========================

def create_socketio(app: Flask) -> SocketIO:
    """Create and configure SocketIO instance"""
    socketio = SocketIO(
        app,
        cors_allowed_origins=os.getenv('CORS_ORIGINS', '*').split(','),
        async_mode='eventlet',
        logger=True,
        engineio_logger=True if app.config['DEBUG'] else False
    )
    
    # Connection handlers
    @socketio.on('connect')
    def handle_connect():
        logger.info(f"WebSocket client connected: {request.sid}")
        emit('connected', {'status': 'connected', 'sid': request.sid})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"WebSocket client disconnected: {request.sid}")
    
    # Room management
    @socketio.on('join')
    def handle_join(data):
        room = data.get('room', 'general')
        join_room(room)
        logger.info(f"Client {request.sid} joined room: {room}")
        emit('joined', {'room': room}, room=room)
    
    @socketio.on('leave')
    def handle_leave(data):
        room = data.get('room', 'general')
        leave_room(room)
        logger.info(f"Client {request.sid} left room: {room}")
    
    # Real-time updates
    @socketio.on('subscribe_updates')
    def handle_subscribe(data):
        """Subscribe to real-time updates"""
        update_type = data.get('type', 'all')
        join_room(f'updates_{update_type}')
        emit('subscribed', {'type': update_type})
    
    @socketio.on('request_status')
    def handle_status_request():
        """Handle status request via WebSocket"""
        from agents.master_orchestrator import MasterOrchestratorAgent
        orchestrator = MasterOrchestratorAgent()
        status = orchestrator.get_system_status()
        emit('status_update', status)
    
    return socketio


# ========================
# Notification Broadcasting
# ========================

class NotificationBroadcaster:
    """Utility for broadcasting notifications via WebSocket"""
    
    _instance = None
    _socketio = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def init(cls, socketio: SocketIO):
        cls._socketio = socketio
    
    @classmethod
    def broadcast(cls, event: str, data: dict, room: str = None):
        """Broadcast notification to clients"""
        if cls._socketio:
            if room:
                cls._socketio.emit(event, data, room=room)
            else:
                cls._socketio.emit(event, data)
    
    @classmethod
    def notify_content_created(cls, content: dict):
        """Notify about new content"""
        cls.broadcast('content_created', content, room='updates_content')
    
    @classmethod
    def notify_content_published(cls, content: dict, platform: str):
        """Notify about published content"""
        cls.broadcast('content_published', {
            'content': content,
            'platform': platform,
            'timestamp': datetime.utcnow().isoformat()
        }, room='updates_schedule')
    
    @classmethod
    def notify_agent_status(cls, agent_name: str, status: dict):
        """Notify about agent status change"""
        cls.broadcast('agent_status', {
            'agent': agent_name,
            'status': status
        }, room='updates_agents')
    
    @classmethod
    def notify_alert(cls, alert: dict):
        """Broadcast system alert"""
        cls.broadcast('system_alert', alert)
    
    @classmethod
    def notify_analytics(cls, analytics: dict):
        """Broadcast analytics update"""
        cls.broadcast('analytics_update', analytics, room='updates_analytics')


# ========================
# Application Entry Point
# ========================

# Create Flask app
app = create_app()

# Create SocketIO
socketio = create_socketio(app)

# Initialize notification broadcaster
NotificationBroadcaster.init(socketio)


if __name__ == '__main__':
    # Get configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Randol's Marketing Platform API")
    logger.info(f"Host: {host}, Port: {port}, Debug: {debug}")
    
    # Run with SocketIO
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )
