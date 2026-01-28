"""
Prompt Templates for Randol's Agentic Marketing Platform
AI prompts library for content generation across all platforms
"""

from typing import Dict, Any, Optional
from datetime import datetime
import random

class PromptTemplates:
    """
    Collection of prompt templates for AI content generation.
    Each template is optimized for specific content types and platforms.
    """
    
    def __init__(self):
        self.specials_rotation = self._load_specials()
        self.storytelling_themes = self._load_storytelling_themes()
        
    def _load_specials(self) -> Dict[str, list]:
        """Load rotating specials by day"""
        return {
            'monday': ['Crawfish Étouffée', 'Boudin Plate', 'Monday Gumbo Special'],
            'tuesday': ['Blackened Catfish', 'Shrimp Po-Boy', 'Crawfish Bisque'],
            'wednesday': ['Fried Seafood Platter', 'Crawfish Pasta', 'Chicken & Sausage Gumbo'],
            'thursday': ['Gulf Shrimp Étouffée', 'Soft Shell Crab', 'Seafood Gumbo'],
            'friday': ['Boiled Crawfish', 'Fried Catfish Platter', 'Seafood Combo'],
            'saturday': ['Weekend Crawfish Boil', 'Prime Rib Special', 'Surf & Turf'],
            'sunday': ['Sunday Brunch Buffet', 'Family Platter', 'Sunday Gumbo']
        }
        
    def _load_storytelling_themes(self) -> list:
        """Load storytelling themes for content"""
        return [
            'family_recipe',
            'local_fishermen',
            'kitchen_secrets',
            'music_tradition',
            'community_stories',
            'seasonal_traditions',
            'chef_spotlight',
            'customer_memories'
        ]
    
    # ========================================
    # MORNING CONTENT TEMPLATES
    # ========================================
    
    def get_morning_greeting_prompt(self, context: Dict[str, Any]) -> str:
        """Generate prompt for morning greeting post"""
        day = context.get('day_of_week', datetime.now().strftime('%A'))
        weather = context.get('weather', {}).get('condition', 'beautiful')
        special = self._get_daily_special(day.lower())
        
        return f"""
Create a warm morning greeting post for Randol's Restaurant.

Context:
- Day: {day}
- Weather: {weather}
- Today's Special: {special}
- Time: Morning (opening)

Requirements:
- Start with a warm Cajun greeting (consider "Where y'at?" or "Good morning, cher!")
- Keep it brief and welcoming (2-3 sentences)
- Hint at today's special or atmosphere
- Include a gentle call to action
- Maintain authentic Louisiana hospitality

Tone: Warm, inviting, like greeting a neighbor
Length: 50-100 words
Platform: Instagram/Facebook
"""

    def get_morning_coffee_prompt(self, context: Dict[str, Any]) -> str:
        """Generate prompt for morning coffee/cafe content"""
        return """
Create a cozy morning coffee moment post for Randol's.

Requirements:
- Capture the morning atmosphere
- Reference the coffee/café culture
- Hint at breakfast options
- Keep it conversational and warm

Tone: Cozy, inviting, peaceful morning energy
Length: 40-80 words
Platform: Instagram Stories
"""

    # ========================================
    # DAILY SPECIAL TEMPLATES
    # ========================================
    
    def get_daily_special_prompt(self, context: Dict[str, Any]) -> str:
        """Generate prompt for daily special promotion"""
        day = context.get('day_of_week', datetime.now().strftime('%A'))
        special = context.get('special_item') or self._get_daily_special(day.lower())
        weather = context.get('weather', {}).get('condition', 'pleasant')
        
        return f"""
Create an appetizing social media post for today's special at Randol's.

Special: {special}
Day: {day}
Weather: {weather}

Requirements:
- Make the dish sound irresistible
- Include sensory descriptions (taste, smell, texture)
- Connect to Louisiana tradition or family recipe
- Add a call to action
- Use "cher" naturally if appropriate
- Keep authentic Cajun voice without stereotypes

Structure:
1. Hook (attention-grabbing opening)
2. Description (make them taste it through words)
3. Heritage connection (brief)
4. Call to action

Length: 80-120 words
Platforms: Instagram, Facebook, Twitter
"""

    def get_special_video_script_prompt(self, context: Dict[str, Any]) -> str:
        """Generate prompt for video script about daily special"""
        special = context.get('special_item', 'Crawfish Étouffée')
        
        return f"""
Write a 30-second video script showcasing {special} at Randol's.

Structure:
- HOOK (0-5 sec): Attention-grabbing visual/statement
- BUILD (5-20 sec): Show the dish, describe what makes it special
- CLIMAX (20-25 sec): The money shot / key selling point
- CTA (25-30 sec): Clear call to action

Requirements:
- Natural Cajun voice-over style
- Include specific sensory details
- Reference family/tradition briefly
- End with compelling CTA

Format:
[VISUAL: description]
VOICE: "dialogue"
[MUSIC: suggestion]
"""

    # ========================================
    # CRAWFISH CONTENT TEMPLATES
    # ========================================
    
    def get_crawfish_content_prompt(self, context: Dict[str, Any]) -> str:
        """Generate prompt for crawfish-specific content"""
        content_angle = random.choice([
            'fresh_arrival',
            'boiling_process', 
            'eating_tips',
            'local_sourcing',
            'season_update',
            'family_tradition'
        ])
        
        angles = {
            'fresh_arrival': "Focus on fresh crawfish arriving today - the excitement, the quality",
            'boiling_process': "Show/describe our secret boiling process and seasoning",
            'eating_tips': "Share tips for eating crawfish like a local (educational but fun)",
            'local_sourcing': "Tell the story of where our crawfish come from (local waters)",
            'season_update': "Update on crawfish season - availability, size, quality",
            'family_tradition': "Connect crawfish to family gatherings and Louisiana tradition"
        }
        
        return f"""
Create engaging crawfish content for Randol's social media.

Angle: {angles[content_angle]}

Requirements:
- Authentic Louisiana voice
- Make readers hungry for crawfish
- Include interesting fact or story
- Natural use of local terms (mudbugs, boil, etc.)
- Call to action

Key phrases to potentially include:
- "Fresh from Louisiana waters"
- "Seasoned with our family blend"
- "Crawfish Capital of the World"
- "Straight from the bayou"

Length: 100-150 words
Best for: Instagram, Facebook, TikTok caption
"""

    def get_crawfish_educational_prompt(self) -> str:
        """Generate prompt for educational crawfish content"""
        return """
Create an educational but entertaining post about crawfish for tourists and newcomers.

Topics to choose from:
- How to eat crawfish properly
- Why Louisiana crawfish are special
- The crawfish season cycle
- Crawfish in Cajun culture
- How to tell if crawfish are fresh

Requirements:
- Be informative without being condescending
- Include practical tips
- Maintain warmth and hospitality
- Invite them to learn more at Randol's

Tone: Friendly teacher / welcoming local expert
Length: 120-180 words
Platform: Instagram Carousel / Facebook
"""

    # ========================================
    # EVENT & MUSIC TEMPLATES
    # ========================================
    
    def get_event_promotion_prompt(self, context: Dict[str, Any]) -> str:
        """Generate prompt for event promotion"""
        event = context.get('event', {})
        event_name = event.get('name', 'Zydeco Night')
        event_date = event.get('date', 'Tonight')
        
        return f"""
Create an exciting event promotion for Randol's:

Event: {event_name}
When: {event_date}

Requirements:
- Build excitement and FOMO
- Emphasize live music and dancing atmosphere
- Mention food + music combo
- Include "Laissez les bon temps rouler!" naturally
- Add reservation/arrival suggestion
- Make people feel they'll miss something special if they don't come

Tone: Celebratory, exciting, community-focused
Length: 80-120 words
Include: Time, what to expect, why it's special
"""

    def get_live_music_prompt(self, context: Dict[str, Any]) -> str:
        """Generate prompt for live music content"""
        band = context.get('band_name', 'tonight\'s band')
        
        return f"""
Promote live zydeco music at Randol's tonight.

Band: {band}

Requirements:
- Capture the energy of live Louisiana music
- Mention the dance floor
- Connect music to food/atmosphere
- Reference the tradition of music at Randol's
- Encourage people to come early for dinner + stay for music

Musical references to consider:
- Zydeco, accordion, washboard
- Two-step dancing
- Fais do-do tradition
- Louisiana sound

Tone: Energetic but welcoming
Length: 60-100 words
"""

    # ========================================
    # STORYTELLING TEMPLATES
    # ========================================
    
    def get_storytelling_prompt(self, context: Dict[str, Any]) -> str:
        """Generate prompt for storytelling content"""
        theme = context.get('theme') or random.choice(self.storytelling_themes)
        
        themes_detail = {
            'family_recipe': "Tell the story of a specific family recipe - who created it, how it's been passed down",
            'local_fishermen': "Share about the local fishermen who supply our fresh seafood",
            'kitchen_secrets': "Reveal a small kitchen secret or technique (but keep some mystery!)",
            'music_tradition': "Connect our music tradition to the history of zydeco",
            'community_stories': "Share a heartwarming customer or community story",
            'seasonal_traditions': "Explain a Louisiana seasonal tradition",
            'chef_spotlight': "Highlight a chef or kitchen staff member",
            'customer_memories': "Share a memorable customer experience"
        }
        
        return f"""
Create a storytelling post for Randol's social media.

Theme: {themes_detail[theme]}

Requirements:
- Tell a genuine, heartfelt story
- Connect to Louisiana culture/heritage
- Make it personal and relatable
- End with invitation to create their own memories
- Keep authentic voice

Structure:
1. Story hook (draw them in)
2. The heart of the story
3. Connection to today/why it matters
4. Warm invitation

Length: 150-250 words
Best for: Facebook long-form, Instagram carousel
"""

    def get_heritage_story_prompt(self) -> str:
        """Generate prompt for heritage/history content"""
        return """
Share a piece of Randol's 50+ year history.

Possible angles:
- How Randol's started
- Evolution of our menu
- The decision to add live music
- Memorable moments over the decades
- Family members who've been part of the journey

Requirements:
- Authentic and genuine
- Pride without boasting
- Include specific details/memories
- Connect past to present
- Honor the Cajun heritage

Tone: Nostalgic, proud, grateful
Length: 150-200 words
"""

    # ========================================
    # PLATFORM-SPECIFIC TEMPLATES
    # ========================================
    
    def get_instagram_reel_script(self, context: Dict[str, Any]) -> str:
        """Generate Instagram Reel script"""
        topic = context.get('topic', 'daily_special')
        
        return f"""
Write an Instagram Reel script about: {topic}

Structure (15-30 seconds):
- HOOK (0-3s): Stop the scroll - bold statement or visual
- CONTENT (3-25s): Main content, quick cuts, engaging
- CTA (25-30s): What do you want them to do?

Requirements:
- Fast-paced but not rushed
- Text overlays suggestions
- Trending audio recommendation if applicable
- Cajun authenticity in voice-over

Format:
[0-3s] HOOK: ...
[3-10s] SCENE 1: ...
[10-20s] SCENE 2: ...
[20-30s] CTA: ...

VOICE-OVER: "..."
TEXT OVERLAY: "..."
"""

    def get_tiktok_script_prompt(self, context: Dict[str, Any]) -> str:
        """Generate TikTok script"""
        return """
Create a TikTok script that could go viral for Randol's.

Trending formats to consider:
- Day in the life at a Cajun restaurant
- How to eat crawfish (tutorial with personality)
- "POV: You're at an authentic Cajun restaurant"
- Behind the scenes in the kitchen
- Louisiana food facts that surprise people

Requirements:
- Hook in first 2 seconds
- Authentic but entertaining
- Educational or entertaining (ideally both)
- Natural Cajun personality
- End with engagement prompt

Length: 15-60 seconds
Include: Hook, content flow, text overlays, music suggestion
"""

    def get_youtube_description_prompt(self, context: Dict[str, Any]) -> str:
        """Generate YouTube video description"""
        video_title = context.get('title', 'A Day at Randol\'s')
        
        return f"""
Write a YouTube description for: {video_title}

Requirements:
- Compelling first 2-3 lines (shows before "more")
- Include timestamps if applicable
- Relevant keywords naturally included
- Links to website/social media
- Call to subscribe
- Louisiana/Cajun relevant hashtags

Structure:
1. Hook paragraph (2-3 sentences)
2. What's in this video
3. Timestamps (if applicable)
4. About Randol's (brief)
5. Links and social handles
6. Hashtags

Length: 200-400 words
"""

    # ========================================
    # EMERGENCY & SPECIAL TEMPLATES
    # ========================================
    
    def get_emergency_content_prompt(self, context: Dict[str, Any]) -> str:
        """Generate emergency/urgent content"""
        situation = context.get('situation', 'general_update')
        tone = context.get('tone', 'professional and reassuring')
        
        return f"""
Create appropriate emergency/urgent content for Randol's.

Situation: {situation}
Required Tone: {tone}

Requirements:
- Address the situation clearly
- Maintain brand voice while being sensitive
- Provide clear, accurate information
- Show care for community
- Include next steps or what to expect

Important:
- Be honest but not alarming
- Maintain warmth even in difficult situations
- Focus on solutions and support
- Represent Randol's values

Length: 50-150 words (clear and direct)
"""

    def get_closure_announcement_prompt(self, context: Dict[str, Any]) -> str:
        """Generate closure announcement (weather, holiday, etc.)"""
        reason = context.get('reason', 'weather')
        duration = context.get('duration', 'today')
        
        return f"""
Announce temporary closure of Randol's.

Reason: {reason}
Duration: {duration}

Requirements:
- Be clear and direct
- Express care for staff and customers
- Maintain warm tone despite disappointing news
- Include when you'll reopen (if known)
- Keep community spirit

Tone: Caring, professional, hopeful
Length: 50-100 words
"""

    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _get_daily_special(self, day: str) -> str:
        """Get a daily special for the given day"""
        specials = self.specials_rotation.get(day, self.specials_rotation['monday'])
        return random.choice(specials)
    
    def get_hashtag_suggestions(self, content_type: str) -> list:
        """Get hashtag suggestions for content type"""
        base = ['#RandolsRestaurant', '#BreauxBridge', '#CajunFood', '#Louisiana']
        
        type_specific = {
            'crawfish': ['#CrawfishBoil', '#Mudbugs', '#CrawfishSeason'],
            'music': ['#ZydecoMusic', '#LiveMusic', '#CajunMusic'],
            'daily_special': ['#DailySpecial', '#LouisianaEats', '#CajunCooking'],
            'event': ['#LaissezLesBonTempsRouler', '#LouisianaMusic', '#CajunDancing'],
            'story': ['#CajunHeritage', '#LouisianaProud', '#FamilyTradition']
        }
        
        return base + type_specific.get(content_type, [])


# Singleton instance
prompt_templates = PromptTemplates()
