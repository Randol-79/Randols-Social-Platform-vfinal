"""
Content Generator Agent - AI-powered content creation with Cajun authenticity
Handles text generation, image creation, video scripting, and platform optimization
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import random
import os

from utils.config import Config
from utils.cajun_voice import CajunVoiceProcessor
from utils.prompt_templates import PromptTemplates
from utils.logger import setup_logger
from utils.prompt_patterns import PromptPatterns, get_platform_requirements
from utils.telemetry import traced, timed, get_marketing_metrics

# Try to import the LLM client
try:
    from utils.llm_client import get_llm_client, LLMClient

    LLM_CLIENT_AVAILABLE = True
except ImportError:
    LLM_CLIENT_AVAILABLE = False

# Try to import OpenAI as fallback
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ContentGeneratorAgent:
    """
    AI-powered content generation agent.
    Creates authentic Cajun content for all social media platforms.
    Uses LLM client with token tracking, cost estimation, and retry logic.
    """

    def __init__(self):
        self.logger = setup_logger("content_generator")
        self.cajun_processor = CajunVoiceProcessor()
        self.templates = PromptTemplates()
        self.prompt_patterns = PromptPatterns()
        self._init_llm_client()
        self.generated_today = 0
        self.status = "active"
        self.metrics = get_marketing_metrics() if LLM_CLIENT_AVAILABLE else None

    def _init_llm_client(self):
        """Initialize LLM client with full tracking capabilities"""
        self.llm_client = None
        self.openai_client = None

        # Prefer the new LLM client with tracking
        if LLM_CLIENT_AVAILABLE:
            try:
                self.llm_client = get_llm_client()
                if self.llm_client.is_available:
                    self.logger.info("LLM client initialized with token tracking")
                    return
            except Exception as e:
                self.logger.warning(f"LLM client initialization failed: {e}")

        # Fallback to direct OpenAI
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                self.logger.info("OpenAI client initialized (fallback mode)")
            except Exception as e:
                self.logger.warning(f"OpenAI initialization failed: {e}")
        else:
            self.logger.warning("No LLM available, using template-based generation")

    async def generate_daily_content(self, context: Dict[str, Any]) -> List[Dict]:
        """Generate daily content based on context"""
        self.logger.info("Starting daily content generation")

        content_plan = self._create_content_plan(context)
        generated_content = []

        for content_type in content_plan:
            try:
                content = await self.generate_content_by_type(content_type, context)
                if content:
                    generated_content.append(content)
                    self.generated_today += 1
            except Exception as e:
                self.logger.error(f"Error generating {content_type}: {e}")

        self.logger.info(f"Generated {len(generated_content)} content items")
        return generated_content

    def _create_content_plan(self, context: Dict[str, Any]) -> List[str]:
        """Create content plan based on context"""
        base_plan = ["morning_greeting", "daily_special", "evening_event"]

        # Add seasonal content
        season = context.get("seasonal_factors", {}).get("season", "regular")
        if "crawfish" in season:
            base_plan.append("crawfish_content")
        elif "mardi_gras" in season:
            base_plan.append("mardi_gras_content")

        # Add event content
        if context.get("local_events"):
            base_plan.append("event_promotion")

        return base_plan

    # Public compatibility wrapper
    def create_content_plan(self, context: Dict[str, Any]) -> List[str]:
        return self._create_content_plan(context)

    # Public wrapper for hashtag generation
    def generate_hashtags(self, keywords: List[str], platform: str = "instagram") -> List[str]:
        return self.cajun_processor.generate_hashtags(keywords, platform)

    @traced("generate_content_by_type")
    @timed("content_generation_duration")
    async def generate_content_by_type(self, content_type: str, context: Dict) -> Optional[Dict]:
        """Generate specific content type using LLM when available"""
        # Try LLM-powered generation first
        if self.llm_client and self.llm_client.is_available:
            try:
                return await self._generate_with_llm(content_type, context)
            except Exception as e:
                self.logger.warning(f"LLM generation failed, falling back to templates: {e}")

        # Fallback to template-based generators
        generators = {
            "morning_greeting": self._generate_morning_greeting,
            "daily_special": self._generate_daily_special,
            "evening_event": self._generate_evening_event,
            "crawfish_content": self._generate_crawfish_content,
            "event_promotion": self._generate_event_promotion,
            "mardi_gras_content": self._generate_mardi_gras_content,
            "storytelling": self._generate_storytelling_content,
        }

        generator = generators.get(content_type, self._generate_generic_content)
        return await generator(context)

    async def _generate_with_llm(self, content_type: str, context: Dict) -> Optional[Dict]:
        """Generate content using LLM with prompt patterns"""
        # Get the content generator prompt
        prompt_template = PromptPatterns.CONTENT_GENERATOR

        # Determine primary platform
        platform = self._get_primary_platform(content_type)
        platform_reqs = get_platform_requirements(platform)

        # Format the prompt
        prompt_data = prompt_template.format(
            content_type=content_type,
            platform=platform,
            day_of_week=context.get("day_of_week", datetime.now().strftime("%A")),
            time_slot=self._get_time_slot(content_type),
            weather=context.get("weather", {}).get("condition", "pleasant"),
            season=context.get("seasonal_factors", {}).get("season", "regular"),
            events=json.dumps(context.get("local_events", [])),
            additional_context=json.dumps(context.get("additional", {})),
            platform_specific_requirements=platform_reqs["requirements"],
        )

        try:
            # Call LLM with JSON response format
            response = await self.llm_client.complete_json_async(
                prompt=prompt_data["user"],
                system_prompt=prompt_data["system"],
                max_tokens=prompt_data["max_tokens"],
                temperature=prompt_data["temperature"],
            )

            # Record metrics
            if self.metrics:
                self.metrics.record_content_generated(content_type, platform)

            # Build content object from LLM response
            return {
                "id": f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": content_type,
                "platforms": self._get_platforms_for_type(content_type),
                "text": response.get("text", ""),
                "hashtags": response.get("hashtags", []),
                "call_to_action": response.get("call_to_action", ""),
                "media_type": self._get_media_type(content_type),
                "scheduling_priority": "high",
                "optimal_time": self._get_optimal_time(content_type),
                "created_at": datetime.now().isoformat(),
                "generation_method": "llm",
                "confidence_score": response.get("confidence_score", 0.8),
                "cajun_phrases_used": response.get("cajun_phrases_used", []),
                "tone": response.get("tone", "warm"),
            }

        except Exception as e:
            self.logger.error(f"LLM content generation failed: {e}")
            raise

    def _get_primary_platform(self, content_type: str) -> str:
        """Get the primary platform for a content type"""
        platform_map = {
            "morning_greeting": "instagram",
            "daily_special": "instagram",
            "evening_event": "facebook",
            "crawfish_content": "instagram",
            "event_promotion": "facebook",
            "mardi_gras_content": "instagram",
            "storytelling": "facebook",
            "generic": "facebook",
        }
        return platform_map.get(content_type, "facebook")

    def _get_platforms_for_type(self, content_type: str) -> List[str]:
        """Get all platforms for a content type"""
        platform_map = {
            "morning_greeting": ["instagram", "facebook"],
            "daily_special": ["instagram", "facebook", "twitter"],
            "evening_event": ["facebook", "instagram"],
            "crawfish_content": ["instagram", "facebook", "tiktok"],
            "event_promotion": ["facebook", "instagram", "google_posts"],
            "mardi_gras_content": ["instagram", "facebook", "tiktok"],
            "storytelling": ["facebook", "instagram"],
            "generic": ["instagram", "facebook"],
        }
        return platform_map.get(content_type, ["instagram", "facebook"])

    def _get_time_slot(self, content_type: str) -> str:
        """Get the time slot for content type"""
        time_slots = {
            "morning_greeting": "morning",
            "daily_special": "lunch",
            "evening_event": "evening",
            "crawfish_content": "afternoon",
            "event_promotion": "afternoon",
            "mardi_gras_content": "morning",
            "storytelling": "evening",
        }
        return time_slots.get(content_type, "afternoon")

    def _get_media_type(self, content_type: str) -> str:
        """Get the recommended media type"""
        media_map = {
            "morning_greeting": "text_with_image",
            "daily_special": "food_photography",
            "evening_event": "event_graphic",
            "crawfish_content": "crawfish_photo",
            "event_promotion": "event_graphic",
            "mardi_gras_content": "festive_photo",
            "storytelling": "nostalgic_photo",
        }
        return media_map.get(content_type, "restaurant_photo")

    def _get_optimal_time(self, content_type: str) -> str:
        """Get optimal posting time for content type"""
        time_map = {
            "morning_greeting": "08:00",
            "daily_special": "11:30",
            "evening_event": "17:00",
            "crawfish_content": "15:00",
            "event_promotion": "12:00",
            "mardi_gras_content": "10:00",
            "storytelling": "19:00",
        }
        return time_map.get(content_type, "14:00")

    async def _generate_morning_greeting(self, context: Dict) -> Dict:
        """Generate morning greeting post"""
        day = context.get("day_of_week", datetime.now().strftime("%A"))
        weather = context.get("weather", {}).get("condition", "beautiful")

        greetings = [
            f"Good morning, y'all! Another {weather.lower()} {day} here in Breaux Bridge. Come start your day with fresh café au lait and some of the best boudin in Acadiana! ☕",
            f"Rise and shine, cher! The kitchen is warming up and the coffee's brewing. It's a beautiful {day} to come see us at Randol's!",
            f"Where y'at? It's a gorgeous {day} morning in the Crawfish Capital of the World. Fresh biscuits are coming out of the oven! 🥐",
            f"Good morning from Randol's, y'all! The {weather.lower()} weather is perfect for breakfast on the bayou. Come hungry, leave happy!",
        ]

        text = random.choice(greetings)

        # Enhance with Cajun authenticity
        text = self.cajun_processor.enhance_cajun_authenticity(text, "morning")

        return {
            "id": f"morning_greeting_{datetime.now().strftime('%Y%m%d')}",
            "type": "morning_greeting",
            "platforms": ["instagram", "facebook"],
            "text": text,
            "hashtags": self.cajun_processor.generate_hashtags(
                ["morning", "breakfast", "cajun"], "instagram"
            ),
            "media_type": "text_with_image",
            "scheduling_priority": "high",
            "optimal_time": "08:00",
            "created_at": datetime.now().isoformat(),
        }

    async def _generate_daily_special(self, context: Dict) -> Dict:
        """Generate daily special promotion"""
        day = context.get("day_of_week", datetime.now().strftime("%A")).lower()

        specials_by_day = {
            "monday": (
                "Crawfish Étouffée",
                "Our Monday special: rich, creamy étouffée made with fresh Louisiana crawfish and our family's secret roux recipe. That's some kinda good, cher!",
            ),
            "tuesday": (
                "Blackened Catfish",
                "Tuesday means fresh blackened catfish, seasoned just right with our Cajun spice blend. Served with dirty rice and collard greens.",
            ),
            "wednesday": (
                "Seafood Gumbo",
                "It's gumbo weather, y'all! Our Wednesday special features the darkest chocolate roux and the freshest Gulf seafood. Come get you some!",
            ),
            "thursday": (
                "Shrimp Po-Boy",
                "Thursday Po-Boy special! Fresh Gulf shrimp, crispy fried, dressed and messy - just the way it should be. That gumbo sings!",
            ),
            "friday": (
                "Boiled Crawfish",
                "Friday night crawfish boil! Fresh mudbugs, seasoned with our secret blend since 1973. Laissez les bon temps rouler!",
            ),
            "saturday": (
                "Weekend Seafood Platter",
                "Saturday feast! Our legendary seafood platter with fried shrimp, oysters, catfish, and all the fixings. Perfect for sharing with family.",
            ),
            "sunday": (
                "Sunday Gumbo Special",
                "Sunday family tradition: our award-winning gumbo, made fresh this morning. Three generations of love in every bowl.",
            ),
        }

        special_name, description = specials_by_day.get(
            day,
            (
                "Chef's Special",
                "Today's chef special is something extraordinary. Come see what's cooking!",
            ),
        )

        return {
            "id": f"daily_special_{datetime.now().strftime('%Y%m%d')}",
            "type": "daily_special",
            "platforms": ["instagram", "facebook", "twitter"],
            "text": f"🍽️ {day.title()} Special: {special_name}\n\n{description}\n\nCome see us, cher! 📍 Breaux Bridge, LA",
            "special_item": special_name,
            "hashtags": self.cajun_processor.generate_hashtags(
                ["dailyspecial", "cajunfood", special_name.lower().replace(" ", "")], "instagram"
            ),
            "media_type": "food_photography",
            "scheduling_priority": "high",
            "optimal_time": "11:30",
            "created_at": datetime.now().isoformat(),
        }

    async def _generate_evening_event(self, context: Dict) -> Dict:
        """Generate evening event content"""
        day = context.get("day_of_week", datetime.now().strftime("%A"))

        evening_content = [
            f"Live zydeco music tonight at Randol's! 🎵 Bring your dancing shoes and an appetite, cher. The band starts at 7pm and the good times roll all night. Laissez les bon temps rouler!",
            f"Tonight at Randol's: live music, cold drinks, and the best Cajun food in Acadiana. Y'all come see us! Two-step on over after dinner! 🎶",
            f"The dance floor is calling, y'all! Live music tonight starting at 7pm. Fresh crawfish, cold beer, and authentic Louisiana vibes. Don't miss it!",
            f"Friday night at Randol's means live zydeco, fresh seafood, and the best company in Breaux Bridge. Save us a dance, cher! 💃🎵",
        ]

        text = random.choice(evening_content)

        return {
            "id": f"evening_event_{datetime.now().strftime('%Y%m%d')}",
            "type": "evening_event",
            "platforms": ["facebook", "instagram"],
            "text": text,
            "hashtags": self.cajun_processor.generate_hashtags(
                ["livemusic", "zydeco", "dancing"], "instagram"
            ),
            "media_type": "event_graphic",
            "scheduling_priority": "high",
            "optimal_time": "17:00",
            "created_at": datetime.now().isoformat(),
        }

    async def _generate_crawfish_content(self, context: Dict) -> Dict:
        """Generate crawfish-specific content"""
        crawfish_posts = [
            "🦞 Fresh mudbugs just arrived from Louisiana waters! Our crawfish are boiled to perfection with our family's secret seasoning blend - spicy enough to make you sweat, but you won't want to stop eating. That's the Cajun way, cher!",
            "Crawfish season is in full swing, y'all! Did you know we go through over 500 pounds of mudbugs on a busy weekend? Fresh, local, and seasoned just right. Come get 'em while they're hot!",
            "There's nothing like a Louisiana crawfish boil. Newspaper on the table, cold beer in hand, good music playing, and the best mudbugs you've ever tasted. That's what we're serving up today at Randol's! 🦞",
            "Let me tell you about our crawfish, cher. Straight from Louisiana waters, seasoned with love, and served hot to your table. Three generations of Randol's have perfected this recipe. Y'all come taste the tradition!",
        ]

        text = random.choice(crawfish_posts)

        return {
            "id": f"crawfish_content_{datetime.now().strftime('%Y%m%d')}",
            "type": "crawfish_content",
            "platforms": ["instagram", "facebook", "tiktok"],
            "text": text,
            "hashtags": self.cajun_processor.generate_hashtags(
                ["crawfish", "mudbugs", "cajunboil"], "instagram"
            ),
            "media_type": "crawfish_photo",
            "scheduling_priority": "high",
            "optimal_time": "15:00",
            "created_at": datetime.now().isoformat(),
        }

    async def _generate_event_promotion(self, context: Dict) -> Dict:
        """Generate event promotion content"""
        events = context.get("local_events", [])
        event = events[0] if events else {"name": "Weekend Special", "type": "food"}

        event_posts = [
            f"🎭 {event['name']} this weekend at Randol's! Live music, dancing, and the best Cajun food in Acadiana. Reserve your table now - this one's gonna be packed, cher! Laissez les bon temps rouler!",
            f"Don't miss {event['name']}! It's one of those nights that makes Randol's special - good food, great music, and even better company. Y'all come see us!",
            f"Mark your calendars, y'all! {event['name']} is happening and you won't want to miss it. Fresh seafood, live zydeco, and authentic Louisiana hospitality. That's what we're all about!",
        ]

        text = random.choice(event_posts)

        return {
            "id": f"event_promo_{datetime.now().strftime('%Y%m%d')}",
            "type": "event_promotion",
            "platforms": ["facebook", "instagram", "google_posts"],
            "text": text,
            "event_data": event,
            "hashtags": self.cajun_processor.generate_hashtags(
                ["event", "livemusic", event["name"].lower().replace(" ", "")], "instagram"
            ),
            "media_type": "event_graphic",
            "scheduling_priority": "high",
            "optimal_time": "12:00",
            "created_at": datetime.now().isoformat(),
        }

    async def _generate_mardi_gras_content(self, context: Dict) -> Dict:
        """Generate Mardi Gras themed content"""
        mardi_gras_posts = [
            "🎭 Laissez les bon temps rouler! It's Mardi Gras season at Randol's! King cake, gumbo, and live zydeco - we've got everything you need to celebrate Carnival the Louisiana way!",
            "Carnival season is here, y'all! Come celebrate with us - special Mardi Gras menu, festive decorations, and that authentic Louisiana spirit. Throw me something, mister! 🎉",
            "It's the most wonderful time of the year in Louisiana - Mardi Gras! Join us for king cake, traditional Cajun cuisine, and the celebration only Acadiana knows how to throw!",
        ]

        text = random.choice(mardi_gras_posts)

        return {
            "id": f"mardi_gras_{datetime.now().strftime('%Y%m%d')}",
            "type": "mardi_gras_content",
            "platforms": ["instagram", "facebook", "tiktok"],
            "text": text,
            "hashtags": self.cajun_processor.generate_hashtags(
                ["mardigras", "carnival", "celebration"], "instagram"
            ),
            "media_type": "festive_photo",
            "scheduling_priority": "high",
            "optimal_time": "10:00",
            "created_at": datetime.now().isoformat(),
        }

    async def _generate_storytelling_content(self, context: Dict) -> Dict:
        """Generate storytelling content"""
        stories = [
            "Let me tell you about our gumbo, cher... This recipe started with Grand-mère Randol back in 1973. She'd stand over that pot for hours, stirring the roux until it was just the right shade of chocolate brown. That patience, that love - it's still in every bowl we serve today. Three generations later, we haven't changed a thing. Some things are too good to mess with.",
            "You know what makes Randol's special? It's not just the food - it's the memories. Families have been celebrating here for 50 years. Anniversaries, graduations, first dates that turned into marriages. These walls have seen a lot of love. And we're grateful for every single story.",
            "My Grand-père always said, 'The secret to good Cajun cooking isn't in the recipe - it's in the patience.' That's why we still make our roux the old way, by hand, taking our time. No shortcuts. Just tradition, passed down through generations.",
        ]

        text = random.choice(stories)

        return {
            "id": f"story_{datetime.now().strftime('%Y%m%d')}",
            "type": "storytelling",
            "platforms": ["facebook", "instagram"],
            "text": text,
            "hashtags": self.cajun_processor.generate_hashtags(
                ["family", "tradition", "heritage"], "instagram"
            ),
            "media_type": "nostalgic_photo",
            "scheduling_priority": "medium",
            "optimal_time": "19:00",
            "created_at": datetime.now().isoformat(),
        }

    async def _generate_generic_content(self, context: Dict) -> Dict:
        """Generate generic content"""
        generic_posts = [
            "Come see us at Randol's today, cher! Fresh Cajun cuisine, warm hospitality, and that authentic Louisiana experience you've been craving. Y'all come back now!",
            "There's always a good reason to visit Randol's - today it's [insert special]. Tomorrow it'll be something else delicious. The day after? You'll just have to come find out!",
            "Life's too short for bad food, y'all. Come eat some good Cajun cooking at Randol's. We'll leave the light on for you!",
        ]

        text = random.choice(generic_posts)

        return {
            "id": f"generic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "generic",
            "platforms": ["instagram", "facebook"],
            "text": text,
            "hashtags": self.cajun_processor.generate_hashtags(
                ["cajunfood", "louisiana"], "instagram"
            ),
            "media_type": "restaurant_photo",
            "scheduling_priority": "low",
            "optimal_time": "14:00",
            "created_at": datetime.now().isoformat(),
        }

    async def generate_emergency_content(self, override_data: Dict) -> Dict:
        """Generate emergency content for crisis situations"""
        reason = override_data.get("reason", "update")
        message = override_data.get("message", "")

        if "weather" in reason.lower() or "storm" in reason.lower():
            text = f"Important update from Randol's: Due to weather conditions, we'll be closed today for the safety of our staff and guests. Stay safe out there, y'all. We'll be back to serving you soon! 🙏"
        elif "closure" in reason.lower():
            text = f"Randol's will be temporarily closed. {message} We appreciate your understanding and can't wait to welcome y'all back soon. Stay tuned for updates!"
        else:
            text = f"Important message from Randol's: {message if message else 'Please check back for updates. Thank you for your patience and continued support, cher!'}"

        return {
            "id": f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "emergency",
            "platforms": override_data.get("platforms", ["facebook", "instagram"]),
            "text": text,
            "priority": "immediate",
            "approval_required": True,
            "created_at": datetime.now().isoformat(),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": "Content Generator",
            "status": self.status,
            "health": "good",
            "openai_available": self.openai_client is not None,
            "generated_today": self.generated_today,
            "last_generation": datetime.now().isoformat(),
            "uptime": "99.5%",
        }

    async def pause(self):
        """Pause the agent"""
        self.status = "paused"
        self.logger.info("Content Generator paused")

    async def resume(self):
        """Resume the agent"""
        self.status = "active"
        self.logger.info("Content Generator resumed")


# Test function
async def test_content_generator():
    generator = ContentGeneratorAgent()

    context = {
        "day_of_week": "Friday",
        "weather": {"condition": "Sunny"},
        "seasonal_factors": {"season": "crawfish_season"},
        "local_events": [{"name": "Zydeco Night", "type": "music"}],
    }

    content = await generator.generate_daily_content(context)
    print(f"Generated {len(content)} content items")

    for item in content:
        print(f"\n--- {item['type']} ---")
        print(item["text"][:200] + "...")


if __name__ == "__main__":
    asyncio.run(test_content_generator())
