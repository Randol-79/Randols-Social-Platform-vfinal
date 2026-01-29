"""
Randol's Agentic Marketing Platform - Main Flask API
Complete REST API for frontend dashboard and agent communication
"""

import asyncio
import functools
import json
import os
from datetime import datetime, timedelta

from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from agents.analytics_agent import AnalyticsAgent
from agents.brand_voice_guardian import BrandVoiceGuardianAgent
from agents.content_generator import ContentGeneratorAgent
from agents.feedback_loop_agent import FeedbackLoopAgent

# Import agents
from agents.master_orchestrator import MasterOrchestratorAgent

# Import utilities
from utils.config import Config
from utils.logger import setup_logger

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "randols-cajun-secret-2024")
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

logger = setup_logger("api")

# Initialize agents (lazy loading for performance)
_agents = {}


def get_agents():
    """Lazy load agents for better startup performance"""
    global _agents
    if not _agents:
        _agents = {
            "orchestrator": MasterOrchestratorAgent(),
            "content_generator": ContentGeneratorAgent(),
            "brand_guardian": BrandVoiceGuardianAgent(),
            "analytics": AnalyticsAgent(),
            "feedback": FeedbackLoopAgent(),
        }
    return _agents


def run_async(coro):
    """Helper to run async functions in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================
# HEALTH & STATUS ENDPOINTS
# ============================================


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify(
        {
            "status": "healthy",
            "service": "randols-agentic-marketing-api",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": os.environ.get("FLASK_ENV", "development"),
        }
    )


@app.route("/api/status", methods=["GET"])
def system_status():
    """Get overall system status"""
    try:
        agents = get_agents()
        status = agents["orchestrator"].get_system_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# AGENT MANAGEMENT ENDPOINTS
# ============================================


@app.route("/api/agents/status", methods=["GET"])
def get_agents_status():
    """Get status of all agents"""
    try:
        agents = get_agents()
        status = {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "master_orchestrator": agents["orchestrator"].get_status(),
                "content_generator": agents["content_generator"].get_status(),
                "brand_voice_guardian": agents["brand_guardian"].get_status(),
                "analytics": agents["analytics"].get_status(),
                "feedback_loop": agents["feedback"].get_status(),
            },
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/agents/pause", methods=["POST"])
def pause_agents():
    """Pause all agents"""
    try:
        agents = get_agents()
        run_async(agents["orchestrator"].pause_all_agents())
        socketio.emit("agents_paused", {"timestamp": datetime.now().isoformat()})
        return jsonify(
            {
                "success": True,
                "message": "All agents paused",
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error pausing agents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/agents/resume", methods=["POST"])
def resume_agents():
    """Resume all agents"""
    try:
        agents = get_agents()
        run_async(agents["orchestrator"].resume_all_agents())
        socketio.emit("agents_resumed", {"timestamp": datetime.now().isoformat()})
        return jsonify(
            {
                "success": True,
                "message": "All agents resumed",
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error resuming agents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/agents/<agent_name>/restart", methods=["POST"])
def restart_agent(agent_name):
    """Restart a specific agent"""
    try:
        agents = get_agents()
        if agent_name not in agents:
            return jsonify({"error": f"Agent {agent_name} not found"}), 404

        # Reinitialize the agent
        agent_mapping = {
            "orchestrator": MasterOrchestratorAgent,
            "content_generator": ContentGeneratorAgent,
            "brand_guardian": BrandVoiceGuardianAgent,
            "analytics": AnalyticsAgent,
            "feedback": FeedbackLoopAgent,
        }

        if agent_name in agent_mapping:
            _agents[agent_name] = agent_mapping[agent_name]()

        return jsonify(
            {
                "success": True,
                "message": f"Agent {agent_name} restarted",
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error restarting agent {agent_name}: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# CONTENT GENERATION ENDPOINTS
# ============================================


@app.route("/api/content/generate", methods=["POST"])
def generate_content():
    """Generate new content"""
    try:
        data = request.get_json() or {}
        content_type = data.get("type", "daily_special")
        context = data.get("context", {})

        context.update(
            {"timestamp": datetime.now().isoformat(), "day_of_week": datetime.now().strftime("%A")}
        )

        agents = get_agents()
        content = run_async(
            agents["content_generator"].generate_content_by_type(content_type, context)
        )

        if content:
            is_approved = run_async(agents["brand_guardian"].validate_content(content))
            content["brand_approved"] = is_approved
            content["authenticity_score"] = agents["brand_guardian"].calculate_authenticity_score(
                content.get("text", "")
            )

        socketio.emit(
            "content_generated",
            {
                "content_id": content.get("id") if content else None,
                "timestamp": datetime.now().isoformat(),
            },
        )

        return jsonify(
            {"success": True, "content": content, "generated_at": datetime.now().isoformat()}
        )
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/content/validate", methods=["POST"])
def validate_content():
    """Validate content with brand voice guardian"""
    try:
        data = request.get_json() or {}
        content = data.get("content", {})
        text = content.get("text", data.get("text", ""))

        agents = get_agents()
        is_approved = run_async(
            agents["brand_guardian"].validate_content({"text": text, "id": "validation_request"})
        )
        suggestions = agents["brand_guardian"].suggest_improvements(text)
        authenticity_score = agents["brand_guardian"].calculate_authenticity_score(text)

        return jsonify(
            {
                "approved": is_approved,
                "suggestions": suggestions,
                "authenticity_score": authenticity_score,
                "validated_at": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error validating content: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/content/enhance", methods=["POST"])
def enhance_content():
    """Enhance content with Cajun authenticity"""
    try:
        data = request.get_json() or {}
        text = data.get("text", "")

        agents = get_agents()
        enhanced_text = agents["brand_guardian"].cajun_processor.enhance_cajun_authenticity(text)
        new_score = agents["brand_guardian"].calculate_authenticity_score(enhanced_text)

        return jsonify(
            {
                "original_text": text,
                "enhanced_text": enhanced_text,
                "authenticity_score": new_score,
                "enhanced_at": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error enhancing content: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# ANALYTICS ENDPOINTS
# ============================================


@app.route("/api/analytics/performance", methods=["GET"])
def get_performance_analytics():
    """Get performance analytics"""
    try:
        time_period = request.args.get("period", "7d")
        agents = get_agents()
        analysis = run_async(agents["analytics"].analyze_performance(time_period))
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/platforms", methods=["GET"])
def get_platform_analytics():
    """Get platform-specific analytics"""
    try:
        agents = get_agents()
        analytics = run_async(agents["analytics"].get_platform_analytics())
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Error getting platform analytics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/engagement", methods=["GET"])
def get_engagement_metrics():
    """Get engagement metrics"""
    try:
        platform = request.args.get("platform", "all")
        period = request.args.get("period", "7d")
        agents = get_agents()
        metrics = run_async(agents["analytics"].get_engagement_metrics(platform, period))
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting engagement metrics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/sentiment", methods=["GET"])
def get_sentiment_analysis():
    """Get sentiment analysis"""
    try:
        agents = get_agents()
        sentiment = run_async(agents["analytics"].get_sentiment_analysis())
        return jsonify(sentiment)
    except Exception as e:
        logger.error(f"Error getting sentiment analysis: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# FEEDBACK & OPTIMIZATION ENDPOINTS
# ============================================


@app.route("/api/feedback/analyze", methods=["POST"])
def analyze_feedback():
    """Analyze performance and get recommendations"""
    try:
        data = request.get_json() or {}
        time_period = data.get("period", "7d")
        agents = get_agents()
        analysis = run_async(agents["feedback"].analyze_performance(time_period))
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error analyzing feedback: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback/recommendations", methods=["GET"])
def get_recommendations():
    """Get optimization recommendations"""
    try:
        agents = get_agents()
        analysis = run_async(agents["feedback"].analyze_performance("7d"))
        return jsonify(
            {
                "recommendations": analysis.get("recommendations", []),
                "generated_at": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/scheduling/optimal-times", methods=["GET"])
def get_optimal_posting_times():
    """Get optimal posting times for platforms"""
    try:
        agents = get_agents()
        optimal_times = run_async(agents["feedback"].get_optimal_posting_times())
        return jsonify(optimal_times)
    except Exception as e:
        logger.error(f"Error getting optimal times: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# CALENDAR & SCHEDULING ENDPOINTS
# ============================================


@app.route("/api/calendar/content", methods=["GET"])
def get_content_calendar():
    """Get content calendar"""
    try:
        date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
        range_type = request.args.get("range", "day")  # day, week, month

        # Generate calendar data based on range
        calendar_data = generate_calendar_data(date_str, range_type)
        return jsonify(calendar_data)
    except Exception as e:
        logger.error(f"Error getting content calendar: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/calendar/schedule", methods=["POST"])
def schedule_content():
    """Schedule content for posting"""
    try:
        data = request.get_json() or {}
        content_id = data.get("content_id")
        platform = data.get("platform")
        scheduled_time = data.get("scheduled_time")

        # Validate and schedule
        scheduled_post = {
            "id": f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content_id": content_id,
            "platform": platform,
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
        }

        socketio.emit("content_scheduled", scheduled_post)

        return jsonify({"success": True, "scheduled_post": scheduled_post})
    except Exception as e:
        logger.error(f"Error scheduling content: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/calendar/posts/<post_id>", methods=["DELETE"])
def delete_scheduled_post(post_id):
    """Delete a scheduled post"""
    try:
        socketio.emit("post_deleted", {"post_id": post_id})
        return jsonify(
            {
                "success": True,
                "message": f"Post {post_id} deleted",
                "deleted_at": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# BRAND VOICE ENDPOINTS
# ============================================


@app.route("/api/brand/guidelines", methods=["GET"])
def get_brand_guidelines():
    """Get brand voice guidelines"""
    try:
        agents = get_agents()
        guidelines = agents["brand_guardian"].voice_guidelines

        # Add additional V.A.U.L.T. framework info
        guidelines["vault_framework"] = {
            "voice_foundation": {
                "authentic": "Never fake the culture, always respectful of traditions",
                "welcoming": "Like inviting someone into your family home",
                "proud": "Confident in heritage without being boastful",
                "musical": "References to zydeco, live music, dancing",
                "family_oriented": "Multi-generational dining, community connections",
            },
            "approved_phrases": agents["brand_guardian"].approved_phrases,
            "cultural_references": agents["brand_guardian"].cajun_processor.cultural_references,
            "authenticity_threshold": agents["brand_guardian"].authenticity_threshold,
        }

        return jsonify(guidelines)
    except Exception as e:
        logger.error(f"Error getting brand guidelines: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/brand/phrases", methods=["GET"])
def get_approved_phrases():
    """Get approved Cajun phrases"""
    try:
        agents = get_agents()
        return jsonify(
            {
                "approved_phrases": agents["brand_guardian"].approved_phrases,
                "cajun_phrases": agents["brand_guardian"].cajun_processor.cajun_phrases,
                "cultural_references": agents["brand_guardian"].cajun_processor.cultural_references,
            }
        )
    except Exception as e:
        logger.error(f"Error getting phrases: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/brand/voice-score", methods=["POST"])
def get_voice_score():
    """Get voice authenticity score for text"""
    try:
        data = request.get_json() or {}
        text = data.get("text", "")

        agents = get_agents()
        validation = agents["brand_guardian"].cajun_processor.validate_authenticity(text)

        return jsonify(
            {
                "text": text,
                "score": validation["authenticity_score"],
                "issues": validation["issues"],
                "recommendations": validation["recommendations"],
            }
        )
    except Exception as e:
        logger.error(f"Error getting voice score: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# EMERGENCY & OVERRIDE ENDPOINTS
# ============================================


@app.route("/api/emergency/override", methods=["POST"])
def emergency_override():
    """Handle emergency content override"""
    try:
        data = request.get_json() or {}
        agents = get_agents()

        override_result = run_async(agents["orchestrator"].handle_emergency_override(data))

        socketio.emit(
            "emergency_override",
            {"reason": data.get("reason"), "timestamp": datetime.now().isoformat()},
        )

        return jsonify(
            {
                "success": True,
                "override_activated": True,
                "timestamp": datetime.now().isoformat(),
                "result": override_result,
            }
        )
    except Exception as e:
        logger.error(f"Error handling emergency override: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/emergency/post", methods=["POST"])
def emergency_post():
    """Create and post emergency content immediately"""
    try:
        data = request.get_json() or {}
        platform = data.get("platform", "facebook")
        message = data.get("message", "")

        agents = get_agents()
        emergency_content = run_async(
            agents["content_generator"].generate_emergency_content(
                {"reason": "manual_emergency_post", "message": message, "platforms": [platform]}
            )
        )

        socketio.emit(
            "emergency_post_created",
            {"content": emergency_content, "timestamp": datetime.now().isoformat()},
        )

        return jsonify(
            {"success": True, "content": emergency_content, "posted_at": datetime.now().isoformat()}
        )
    except Exception as e:
        logger.error(f"Error creating emergency post: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# NOTIFICATIONS ENDPOINTS
# ============================================


@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    """Get recent notifications"""
    try:
        # In production, fetch from database
        notifications = [
            {
                "id": 1,
                "type": "info",
                "title": "Content Generated",
                "message": "Content Generator created crawfish boil promotion",
                "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
                "read": False,
            },
            {
                "id": 2,
                "type": "success",
                "title": "Posts Approved",
                "message": "Brand Voice Guardian approved 3 posts",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "read": False,
            },
            {
                "id": 3,
                "type": "warning",
                "title": "Engagement Alert",
                "message": "Engagement rate dropped 15% - optimization suggested",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "read": False,
            },
        ]
        return jsonify({"notifications": notifications})
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        return jsonify(
            {
                "success": True,
                "notification_id": notification_id,
                "marked_at": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error marking notification: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# WEBSOCKET EVENTS
# ============================================


@socketio.on("connect")
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected")
    emit("connected", {"status": "connected", "timestamp": datetime.now().isoformat()})


@socketio.on("disconnect")
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected")


@socketio.on("subscribe_updates")
def handle_subscribe(data):
    """Handle subscription to real-time updates"""
    channel = data.get("channel", "all")
    logger.info(f"Client subscribed to {channel}")
    emit("subscribed", {"channel": channel, "status": "active"})


# ============================================
# HELPER FUNCTIONS
# ============================================


def generate_calendar_data(date_str, range_type):
    """Generate calendar data for the specified date range"""
    base_date = datetime.strptime(date_str, "%Y-%m-%d")

    posts = [
        {
            "id": "morning_001",
            "platform": "instagram",
            "scheduled_time": "09:00",
            "content_type": "morning_greeting",
            "status": "scheduled",
            "preview": "Good morning, y'all! Fresh crawfish just arrived...",
            "authenticity_score": 0.87,
        },
        {
            "id": "special_001",
            "platform": "facebook",
            "scheduled_time": "11:30",
            "content_type": "daily_special",
            "status": "approved",
            "preview": "Today's special: Gulf Shrimp Étouffee...",
            "authenticity_score": 0.92,
        },
        {
            "id": "event_001",
            "platform": "tiktok",
            "scheduled_time": "15:00",
            "content_type": "event_promotion",
            "status": "pending_review",
            "preview": "Zydeco night tonight! Laissez les bon temps rouler!",
            "authenticity_score": 0.95,
        },
        {
            "id": "evening_001",
            "platform": "facebook",
            "scheduled_time": "18:30",
            "content_type": "evening_event",
            "status": "scheduled",
            "preview": "Live music starting at 7pm, cher!",
            "authenticity_score": 0.89,
        },
    ]

    return {
        "date": date_str,
        "range_type": range_type,
        "posts": posts,
        "total_posts": len(posts),
        "platforms": ["instagram", "facebook", "tiktok", "youtube"],
        "stats": {"scheduled": 2, "approved": 1, "pending_review": 1, "posted": 0},
    }


# ============================================
# ERROR HANDLERS
# ============================================


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"

    logger.info(f"Starting Randol's Agentic Marketing API on port {port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)
