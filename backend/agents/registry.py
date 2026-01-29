"""
Agent Registry - Singleton pattern for agent management
Provides centralized access to all agents with lazy initialization
"""

import threading
from typing import Dict, Any, Optional, Type
from utils.logger import setup_logger

logger = setup_logger("agent_registry")


class AgentRegistry:
    """
    Singleton registry for managing agent instances.
    Ensures each agent is instantiated only once and provides
    thread-safe access to all agents.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            self._agents: Dict[str, Any] = {}
            self._agent_classes: Dict[str, str] = {
                "master_orchestrator": "agents.master_orchestrator.MasterOrchestratorAgent",
                "content_generator": "agents.content_generator.ContentGeneratorAgent",
                "brand_voice_guardian": "agents.brand_voice_guardian.BrandVoiceGuardianAgent",
                "analytics": "agents.analytics_agent.AnalyticsAgent",
                "feedback_loop": "agents.feedback_loop_agent.FeedbackLoopAgent",
                "scheduler": "agents.scheduler_agent.SchedulerAgent",
            }
            self._initialized = True
            logger.info("Agent registry initialized")

    def _import_agent_class(self, class_path: str) -> Optional[Type]:
        """Dynamically import an agent class"""
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            import importlib

            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except Exception as e:
            logger.error(f"Failed to import agent class {class_path}: {e}")
            return None

    def get(self, agent_name: str) -> Optional[Any]:
        """
        Get an agent instance by name.
        Creates the instance if it doesn't exist (lazy initialization).
        """
        if agent_name not in self._agent_classes:
            logger.warning(f"Unknown agent: {agent_name}")
            return None

        if agent_name not in self._agents:
            with self._lock:
                # Double-check after acquiring lock
                if agent_name not in self._agents:
                    class_path = self._agent_classes[agent_name]
                    agent_class = self._import_agent_class(class_path)
                    if agent_class:
                        try:
                            self._agents[agent_name] = agent_class()
                            logger.info(f"Initialized agent: {agent_name}")
                        except Exception as e:
                            logger.error(f"Failed to instantiate {agent_name}: {e}")
                            return None
                    else:
                        return None

        return self._agents.get(agent_name)

    def get_orchestrator(self):
        """Get the master orchestrator agent"""
        return self.get("master_orchestrator")

    def get_content_generator(self):
        """Get the content generator agent"""
        return self.get("content_generator")

    def get_brand_voice_guardian(self):
        """Get the brand voice guardian agent"""
        return self.get("brand_voice_guardian")

    def get_analytics(self):
        """Get the analytics agent"""
        return self.get("analytics")

    def get_feedback_loop(self):
        """Get the feedback loop agent"""
        return self.get("feedback_loop")

    def get_scheduler(self):
        """Get the scheduler agent"""
        return self.get("scheduler")

    def list_agents(self) -> Dict[str, str]:
        """List all registered agent names and their status"""
        status = {}
        for name in self._agent_classes:
            if name in self._agents:
                agent = self._agents[name]
                if hasattr(agent, "get_status"):
                    agent_status = agent.get_status()
                    status[name] = agent_status.get("status", "active")
                else:
                    status[name] = "active"
            else:
                status[name] = "not_initialized"
        return status

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all initialized agents"""
        statuses = {}
        for name, agent in self._agents.items():
            if hasattr(agent, "get_status"):
                statuses[name] = agent.get_status()
            else:
                statuses[name] = {"status": "active", "health": "unknown"}
        return statuses

    async def pause_all(self):
        """Pause all agents"""
        for name, agent in self._agents.items():
            if hasattr(agent, "pause"):
                try:
                    await agent.pause()
                    logger.info(f"Paused agent: {name}")
                except Exception as e:
                    logger.error(f"Failed to pause {name}: {e}")

    async def resume_all(self):
        """Resume all agents"""
        for name, agent in self._agents.items():
            if hasattr(agent, "resume"):
                try:
                    await agent.resume()
                    logger.info(f"Resumed agent: {name}")
                except Exception as e:
                    logger.error(f"Failed to resume {name}: {e}")

    def reset(self):
        """Reset the registry (useful for testing)"""
        with self._lock:
            self._agents.clear()
            logger.info("Agent registry reset")


# Global registry instance
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


def get_agent(name: str) -> Optional[Any]:
    """Convenience function to get an agent by name"""
    return get_registry().get(name)
