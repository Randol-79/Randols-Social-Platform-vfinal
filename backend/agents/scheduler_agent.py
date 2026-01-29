"""
Scheduler Agent - Content Scheduling, Queue Management, and Optimal Timing
Handles automated posting, scheduling optimization, and calendar management
"""

import asyncio
import heapq
import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from utils.config import Config
from utils.logger import setup_logger


class SchedulerAgent:
    """Content scheduling and queue management agent"""

    def __init__(self):
        self.logger = setup_logger("scheduler")
        self.content_queue: List[Dict] = []
        self.scheduled_posts: Dict[str, Dict] = {}
        self.posting_schedule = Config.POSTING_SCHEDULE
        self.platform_cooldowns: Dict[str, datetime] = {}
        self.status = "active"
        self.is_paused = False
        self.daily_post_count = 0
        self.last_reset_date = datetime.now().date()

        # Priority queue for scheduled posts (min-heap by scheduled time)
        self._priority_queue: List[tuple] = []

        # Platform-specific constraints
        self.platform_limits = {
            "instagram": {"daily": 10, "hourly": 2, "min_interval": 30},
            "facebook": {"daily": 15, "hourly": 3, "min_interval": 20},
            "tiktok": {"daily": 5, "hourly": 1, "min_interval": 60},
            "youtube": {"daily": 3, "hourly": 1, "min_interval": 120},
            "google_posts": {"daily": 5, "hourly": 2, "min_interval": 60},
        }

        # Track posts per platform
        self.platform_post_counts = defaultdict(
            lambda: {"daily": 0, "hourly": 0, "last_hour": None}
        )

    async def schedule_content(
        self, content: Dict[str, Any], scheduled_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Schedule content for posting"""
        try:
            # Generate unique ID
            content_id = content.get("id", f"content_{datetime.now().strftime('%Y%m%d%H%M%S')}")

            # Determine optimal time if not specified
            if scheduled_time is None:
                scheduled_time = self._calculate_optimal_time(content)

            # Validate scheduling
            validation = self._validate_scheduling(content, scheduled_time)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["reason"],
                    "suggested_time": validation.get("suggested_time"),
                }

            # Create scheduled post entry
            scheduled_post = {
                "id": content_id,
                "content": content,
                "scheduled_time": scheduled_time.isoformat(),
                "platforms": content.get("platforms", ["instagram", "facebook"]),
                "status": "scheduled",
                "created_at": datetime.now().isoformat(),
                "priority": content.get("scheduling_priority", "normal"),
                "retries": 0,
                "max_retries": 3,
            }

            # Add to storage and queue
            self.scheduled_posts[content_id] = scheduled_post
            heapq.heappush(self._priority_queue, (scheduled_time.timestamp(), content_id))

            self.logger.info(f"Content scheduled: {content_id} for {scheduled_time.isoformat()}")

            return {
                "success": True,
                "post_id": content_id,
                "scheduled_time": scheduled_time.isoformat(),
                "platforms": scheduled_post["platforms"],
            }

        except Exception as e:
            self.logger.error(f"Error scheduling content: {str(e)}")
            return {"success": False, "error": str(e)}

    def _calculate_optimal_time(self, content: Dict[str, Any]) -> datetime:
        """Calculate optimal posting time based on content type and analytics"""
        now = datetime.now()
        content_type = content.get("type", "general")
        platforms = content.get("platforms", ["instagram", "facebook"])

        # Time preferences by content type
        time_preferences = {
            "morning_greeting": {"hour": 8, "minute": 0},
            "daily_special": {"hour": 11, "minute": 30},
            "lunch_promo": {"hour": 11, "minute": 0},
            "evening_event": {"hour": 17, "minute": 0},
            "live_music": {"hour": 18, "minute": 30},
            "crawfish_education": {"hour": 15, "minute": 0},
            "event_promotion": {"hour": 17, "minute": 0},
            "weekend_special": {"hour": 10, "minute": 0},
        }

        # Get base time preference
        pref = time_preferences.get(content_type, {"hour": 12, "minute": 0})
        optimal_time = now.replace(
            hour=pref["hour"], minute=pref["minute"], second=0, microsecond=0
        )

        # If time has passed today, schedule for tomorrow
        if optimal_time <= now:
            optimal_time += timedelta(days=1)

        # Adjust for platform-specific optimal times
        platform_adjustments = self._get_platform_optimal_adjustment(
            platforms[0] if platforms else "instagram"
        )
        optimal_time += timedelta(minutes=platform_adjustments)

        # Avoid scheduling conflicts
        optimal_time = self._find_available_slot(optimal_time, platforms)

        return optimal_time

    def _get_platform_optimal_adjustment(self, platform: str) -> int:
        """Get platform-specific time adjustment in minutes"""
        # Based on engagement data patterns
        adjustments = {
            "instagram": 0,  # Peak at standard times
            "facebook": 15,  # Slightly later
            "tiktok": -30,  # Earlier for younger audience
            "youtube": 30,  # Longer buffer for processing
            "google_posts": 0,
        }
        return adjustments.get(platform, 0)

    def _find_available_slot(self, preferred_time: datetime, platforms: List[str]) -> datetime:
        """Find available time slot avoiding conflicts"""
        slot = preferred_time
        max_attempts = 48  # Max 24 hours of checking

        for _ in range(max_attempts):
            conflict = False
            for platform in platforms:
                if not self._check_platform_availability(platform, slot):
                    conflict = True
                    break

            if not conflict:
                return slot

            # Move to next 30-minute slot
            slot += timedelta(minutes=30)

        return preferred_time  # Fallback to original if no slot found

    def _check_platform_availability(self, platform: str, time: datetime) -> bool:
        """Check if platform is available for posting at given time"""
        limits = self.platform_limits.get(platform, {"min_interval": 30})

        # Check cooldown
        last_post = self.platform_cooldowns.get(platform)
        if last_post:
            min_interval = timedelta(minutes=limits["min_interval"])
            if time - last_post < min_interval:
                return False

        # Check for existing scheduled posts at same time
        for post_id, post in self.scheduled_posts.items():
            if post["status"] == "scheduled":
                post_time = datetime.fromisoformat(post["scheduled_time"])
                if platform in post["platforms"]:
                    if abs((post_time - time).total_seconds()) < 1800:  # 30 min buffer
                        return False

        return True

    def _validate_scheduling(self, content: Dict, scheduled_time: datetime) -> Dict[str, Any]:
        """Validate scheduling request"""
        now = datetime.now()

        # Check if time is in the future
        if scheduled_time <= now:
            return {
                "valid": False,
                "reason": "Scheduled time must be in the future",
                "suggested_time": (now + timedelta(hours=1)).isoformat(),
            }

        # Check if not too far in future (max 30 days)
        max_future = now + timedelta(days=30)
        if scheduled_time > max_future:
            return {
                "valid": False,
                "reason": "Cannot schedule more than 30 days in advance",
                "suggested_time": max_future.isoformat(),
            }

        # Check platform limits
        platforms = content.get("platforms", [])
        for platform in platforms:
            limits = self.platform_limits.get(platform, {})
            counts = self.platform_post_counts[platform]

            if counts["daily"] >= limits.get("daily", 999):
                return {
                    "valid": False,
                    "reason": f"Daily post limit reached for {platform}",
                    "suggested_time": (now + timedelta(days=1))
                    .replace(hour=9, minute=0)
                    .isoformat(),
                }

        return {"valid": True}

    async def get_pending_posts(self, hours_ahead: int = 24) -> List[Dict]:
        """Get posts scheduled within the next N hours"""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours_ahead)

        pending = []
        for post_id, post in self.scheduled_posts.items():
            if post["status"] == "scheduled":
                post_time = datetime.fromisoformat(post["scheduled_time"])
                if now <= post_time <= cutoff:
                    pending.append(post)

        # Sort by scheduled time
        pending.sort(key=lambda x: x["scheduled_time"])
        return pending

    async def get_due_posts(self) -> List[Dict]:
        """Get posts that are due for publishing"""
        now = datetime.now()
        due_posts = []

        while self._priority_queue:
            timestamp, post_id = self._priority_queue[0]
            scheduled_time = datetime.fromtimestamp(timestamp)

            if scheduled_time <= now:
                heapq.heappop(self._priority_queue)
                post = self.scheduled_posts.get(post_id)
                if post and post["status"] == "scheduled":
                    due_posts.append(post)
            else:
                break

        return due_posts

    async def process_due_posts(self, platform_manager) -> List[Dict]:
        """Process and publish due posts"""
        if self.is_paused:
            return []

        due_posts = await self.get_due_posts()
        results = []

        for post in due_posts:
            try:
                # Mark as processing
                post["status"] = "processing"

                # Publish to platforms
                content = post["content"]
                platforms = post["platforms"]

                publish_results = await platform_manager.post_to_platforms(content, platforms)

                # Update post status based on results
                all_success = all(r.get("success", False) for r in publish_results.values())

                if all_success:
                    post["status"] = "published"
                    post["published_at"] = datetime.now().isoformat()
                    post["publish_results"] = publish_results

                    # Update platform cooldowns
                    for platform in platforms:
                        self.platform_cooldowns[platform] = datetime.now()
                        self.platform_post_counts[platform]["daily"] += 1

                    self.logger.info(f"Successfully published: {post['id']}")
                else:
                    # Handle partial failure or retry
                    post["retries"] += 1
                    if post["retries"] < post["max_retries"]:
                        post["status"] = "retry_scheduled"
                        retry_time = datetime.now() + timedelta(minutes=15)
                        post["scheduled_time"] = retry_time.isoformat()
                        heapq.heappush(self._priority_queue, (retry_time.timestamp(), post["id"]))
                        self.logger.warning(f"Retry scheduled for: {post['id']}")
                    else:
                        post["status"] = "failed"
                        post["failure_reason"] = "Max retries exceeded"
                        self.logger.error(f"Post failed after max retries: {post['id']}")

                results.append(
                    {"post_id": post["id"], "status": post["status"], "results": publish_results}
                )

            except Exception as e:
                self.logger.error(f"Error processing post {post['id']}: {str(e)}")
                post["status"] = "error"
                post["error"] = str(e)
                results.append({"post_id": post["id"], "status": "error", "error": str(e)})

        return results

    async def cancel_scheduled_post(self, post_id: str) -> Dict[str, Any]:
        """Cancel a scheduled post"""
        post = self.scheduled_posts.get(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}

        if post["status"] not in ["scheduled", "retry_scheduled"]:
            return {"success": False, "error": f"Cannot cancel post with status: {post['status']}"}

        post["status"] = "cancelled"
        post["cancelled_at"] = datetime.now().isoformat()

        self.logger.info(f"Post cancelled: {post_id}")
        return {"success": True, "post_id": post_id}

    async def reschedule_post(self, post_id: str, new_time: datetime) -> Dict[str, Any]:
        """Reschedule a post to a new time"""
        post = self.scheduled_posts.get(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}

        if post["status"] not in ["scheduled", "retry_scheduled", "failed"]:
            return {
                "success": False,
                "error": f"Cannot reschedule post with status: {post['status']}",
            }

        # Validate new time
        validation = self._validate_scheduling(post["content"], new_time)
        if not validation["valid"]:
            return {"success": False, "error": validation["reason"]}

        # Update post
        old_time = post["scheduled_time"]
        post["scheduled_time"] = new_time.isoformat()
        post["status"] = "scheduled"
        post["retries"] = 0
        post["rescheduled_at"] = datetime.now().isoformat()

        # Add to priority queue
        heapq.heappush(self._priority_queue, (new_time.timestamp(), post_id))

        self.logger.info(f"Post rescheduled: {post_id} from {old_time} to {new_time.isoformat()}")
        return {
            "success": True,
            "post_id": post_id,
            "old_time": old_time,
            "new_time": new_time.isoformat(),
        }

    def get_calendar_view(self, start_date: datetime, end_date: datetime) -> Dict[str, List[Dict]]:
        """Get calendar view of scheduled content"""
        calendar = defaultdict(list)

        for post_id, post in self.scheduled_posts.items():
            if post["status"] in ["scheduled", "published", "processing"]:
                post_time = datetime.fromisoformat(post["scheduled_time"])
                if start_date <= post_time <= end_date:
                    date_key = post_time.strftime("%Y-%m-%d")
                    calendar[date_key].append(
                        {
                            "id": post_id,
                            "time": post_time.strftime("%H:%M"),
                            "type": post["content"].get("type", "general"),
                            "platforms": post["platforms"],
                            "status": post["status"],
                            "text_preview": post["content"].get("text", "")[:100] + "...",
                        }
                    )

        # Sort each day's posts by time
        for date_key in calendar:
            calendar[date_key].sort(key=lambda x: x["time"])

        return dict(calendar)

    def get_optimal_times(self, platform: str, content_type: str) -> List[Dict]:
        """Get recommended optimal posting times"""
        # Based on engagement analytics (simulated)
        optimal_times = {
            "instagram": {
                "morning_greeting": [
                    {"time": "08:00", "score": 0.85},
                    {"time": "08:30", "score": 0.82},
                ],
                "daily_special": [
                    {"time": "11:30", "score": 0.90},
                    {"time": "12:00", "score": 0.87},
                ],
                "evening_event": [
                    {"time": "17:00", "score": 0.88},
                    {"time": "17:30", "score": 0.85},
                ],
                "general": [{"time": "12:00", "score": 0.80}, {"time": "18:00", "score": 0.78}],
            },
            "facebook": {
                "morning_greeting": [
                    {"time": "08:30", "score": 0.82},
                    {"time": "09:00", "score": 0.80},
                ],
                "daily_special": [
                    {"time": "11:00", "score": 0.88},
                    {"time": "11:30", "score": 0.86},
                ],
                "evening_event": [
                    {"time": "16:30", "score": 0.85},
                    {"time": "17:00", "score": 0.83},
                ],
                "general": [{"time": "13:00", "score": 0.78}, {"time": "19:00", "score": 0.76}],
            },
            "tiktok": {
                "general": [{"time": "19:00", "score": 0.92}, {"time": "21:00", "score": 0.90}],
                "daily_special": [
                    {"time": "12:00", "score": 0.85},
                    {"time": "18:00", "score": 0.88},
                ],
            },
        }

        platform_times = optimal_times.get(platform, optimal_times["instagram"])
        return platform_times.get(content_type, platform_times.get("general", []))

    def pause(self):
        """Pause the scheduler"""
        self.is_paused = True
        self.status = "paused"
        self.logger.info("Scheduler paused")

    def resume(self):
        """Resume the scheduler"""
        self.is_paused = False
        self.status = "active"
        self.logger.info("Scheduler resumed")

    def _reset_daily_counters(self):
        """Reset daily counters if it's a new day"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.last_reset_date = today
            self.daily_post_count = 0
            for platform in self.platform_post_counts:
                self.platform_post_counts[platform]["daily"] = 0
            self.logger.info("Daily counters reset")

    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        self._reset_daily_counters()

        # Count posts by status
        status_counts = defaultdict(int)
        for post in self.scheduled_posts.values():
            status_counts[post["status"]] += 1

        return {
            "status": self.status,
            "is_paused": self.is_paused,
            "total_scheduled": len(self.scheduled_posts),
            "pending": status_counts["scheduled"],
            "published_today": status_counts["published"],
            "failed": status_counts["failed"],
            "queue_size": len(self._priority_queue),
            "platform_counts": dict(self.platform_post_counts),
            "last_reset": self.last_reset_date.isoformat(),
        }

    def get_queue_preview(self, limit: int = 10) -> List[Dict]:
        """Preview upcoming posts in queue"""
        preview = []
        temp_queue = self._priority_queue.copy()

        while temp_queue and len(preview) < limit:
            timestamp, post_id = heapq.heappop(temp_queue)
            post = self.scheduled_posts.get(post_id)
            if post and post["status"] == "scheduled":
                preview.append(
                    {
                        "id": post_id,
                        "scheduled_time": post["scheduled_time"],
                        "platforms": post["platforms"],
                        "type": post["content"].get("type", "general"),
                        "priority": post.get("priority", "normal"),
                    }
                )

        return preview


class ContentQueue:
    """Priority queue for content management"""

    def __init__(self):
        self.logger = setup_logger("content_queue")
        self._queue: List[tuple] = []  # (priority, timestamp, content)
        self._processed = set()

    def add(self, content: Dict[str, Any], priority: int = 5) -> str:
        """Add content to queue (lower priority number = higher priority)"""
        content_id = content.get("id", f"q_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
        timestamp = datetime.now().timestamp()

        heapq.heappush(self._queue, (priority, timestamp, content_id, content))
        self.logger.debug(f"Added to queue: {content_id} with priority {priority}")

        return content_id

    def pop(self) -> Optional[Dict[str, Any]]:
        """Get highest priority content from queue"""
        while self._queue:
            priority, timestamp, content_id, content = heapq.heappop(self._queue)
            if content_id not in self._processed:
                self._processed.add(content_id)
                return content
        return None

    def peek(self) -> Optional[Dict[str, Any]]:
        """Peek at highest priority content without removing"""
        if self._queue:
            return self._queue[0][3]
        return None

    def size(self) -> int:
        """Get queue size"""
        return len(self._queue)

    def clear(self):
        """Clear the queue"""
        self._queue.clear()
        self._processed.clear()
        self.logger.info("Queue cleared")

    def get_all(self) -> List[Dict]:
        """Get all items in queue without removing"""
        return [item[3] for item in sorted(self._queue)]


# Background scheduler runner
async def run_scheduler_loop(
    scheduler: SchedulerAgent, platform_manager, interval_seconds: int = 60
):
    """Background loop to process scheduled posts"""
    logger = setup_logger("scheduler_loop")
    logger.info("Starting scheduler loop")

    while True:
        try:
            if not scheduler.is_paused:
                results = await scheduler.process_due_posts(platform_manager)
                if results:
                    logger.info(f"Processed {len(results)} posts")
        except Exception as e:
            logger.error(f"Scheduler loop error: {str(e)}")

        await asyncio.sleep(interval_seconds)
