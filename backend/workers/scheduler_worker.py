"""
Scheduler Worker - Background worker for processing scheduled posts
Runs continuously and processes due posts from the queue
"""

import asyncio
import signal
import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.logger import setup_logger
from agents.scheduler_agent import SchedulerAgent
from agents.platform_agents import PlatformAgentManager


class SchedulerWorker:
    """Background worker for content scheduling"""

    def __init__(self):
        self.logger = setup_logger("scheduler_worker")
        self.scheduler = SchedulerAgent()
        self.platform_manager = PlatformAgentManager()
        self.running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None

        # Configuration
        self.check_interval = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", 60))
        self.health_check_interval = 300  # 5 minutes

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    async def start(self):
        """Start the worker"""
        self.running = True
        self.logger.info("=" * 50)
        self.logger.info("Scheduler Worker Starting")
        self.logger.info(f"Check interval: {self.check_interval}s")
        self.logger.info("=" * 50)

        # Run initial status check
        await self._log_status()

        # Main worker loop
        last_health_check = datetime.now()

        while self.running:
            try:
                # Process due posts
                await self._process_due_posts()

                # Periodic health check
                if (
                    datetime.now() - last_health_check
                ).total_seconds() > self.health_check_interval:
                    await self._log_status()
                    last_health_check = datetime.now()

                # Wait for next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(self.check_interval)

        # Cleanup
        await self._shutdown()

    async def _process_due_posts(self):
        """Process posts that are due for publishing"""
        try:
            results = await self.scheduler.process_due_posts(self.platform_manager)

            if results:
                self.logger.info(f"Processed {len(results)} posts")
                for result in results:
                    status = result.get("status", "unknown")
                    post_id = result.get("post_id", "unknown")

                    if status == "published":
                        self.logger.info(f"✓ Published: {post_id}")
                    elif status == "failed":
                        self.logger.error(f"✗ Failed: {post_id}")
                    elif status == "retry_scheduled":
                        self.logger.warning(f"↻ Retry scheduled: {post_id}")

        except Exception as e:
            self.logger.error(f"Error processing due posts: {str(e)}")

    async def _log_status(self):
        """Log current worker status"""
        try:
            scheduler_status = self.scheduler.get_status()
            platform_status = self.platform_manager.get_all_status()

            self.logger.info("-" * 40)
            self.logger.info("Worker Status Report")
            self.logger.info(f"Scheduler: {scheduler_status['status']}")
            self.logger.info(f"Pending posts: {scheduler_status['pending']}")
            self.logger.info(f"Published today: {scheduler_status['published_today']}")
            self.logger.info(f"Queue size: {scheduler_status['queue_size']}")

            for platform, status in platform_status.items():
                self.logger.info(
                    f"  {platform}: {status['status']} ({status['posts_today']} posts today)"
                )

            self.logger.info("-" * 40)

        except Exception as e:
            self.logger.error(f"Error getting status: {str(e)}")

    async def _shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down scheduler worker...")

        try:
            # Close platform sessions
            await self.platform_manager.close_all()
            self.logger.info("Platform sessions closed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")

        self.logger.info("Scheduler worker stopped")


def main():
    """Main entry point"""
    worker = SchedulerWorker()

    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        print("\nWorker interrupted")
    except Exception as e:
        print(f"Worker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
