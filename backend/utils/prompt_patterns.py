"""
Prompt Patterns for LLM-Coordinated Agent Workflows
Implements GENERATOR_PROMPT, VALIDATOR_PROMPT, LLM-as-a-Judge patterns
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class PromptRole(Enum):
    GENERATOR = "generator"
    VALIDATOR = "validator"
    JUDGE = "judge"
    FEEDBACK = "feedback"


@dataclass
class PromptTemplate:
    """Structured prompt template with metadata"""
    name: str
    role: PromptRole
    system_prompt: str
    user_template: str
    expected_output_format: str
    max_tokens: int = 500
    temperature: float = 0.7

    def format(self, **kwargs) -> Dict[str, str]:
        """Format the prompt with provided context"""
        return {
            "system": self.system_prompt,
            "user": self.user_template.format(**kwargs),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }


class PromptPatterns:
    """
    Collection of prompt patterns for the Randol's marketing platform.
    Implements best practices for LLM-coordinated workflows.
    """

    # =========================================
    # GENERATOR PROMPTS
    # =========================================

    CONTENT_GENERATOR = PromptTemplate(
        name="content_generator",
        role=PromptRole.GENERATOR,
        system_prompt="""You are a Cajun content creator for Randol's Restaurant in Breaux Bridge, Louisiana.

Your voice guidelines (V.A.U.L.T. Framework):
- Voice Foundation: Authentic Cajun hospitality - warm, welcoming, like family
- Audience Adaptations: Adjust formality based on platform (Instagram: casual, Facebook: community-focused)
- Unique Flavor: Use natural Cajun expressions (y'all, cher, laissez les bon temps rouler)
- Language Patterns: Conversational, storytelling tone, reference local culture
- Tone Requirements: Always warm, never salesy. Share stories, not pitches.

Cultural guidelines:
- Reference zydeco music, crawfish boils, and family traditions authentically
- Avoid stereotypes or exaggerated accents
- Celebrate Louisiana heritage with pride and respect

Restaurant context:
- Established 1973, family-owned for three generations
- Famous for crawfish, live zydeco music, and authentic Cajun cuisine
- Located in "Crawfish Capital of the World" - Breaux Bridge, LA""",

        user_template="""Generate {content_type} content for {platform}.

Context:
- Day: {day_of_week}
- Time of day: {time_slot}
- Weather: {weather}
- Season: {season}
- Special events: {events}
- Additional context: {additional_context}

Requirements:
- Create authentic, engaging content that reflects Randol's voice
- Include 1-2 natural Cajun expressions
- Make it feel personal and inviting
- {platform_specific_requirements}

Output as JSON:
{{
    "text": "The main content text",
    "hashtags": ["relevant", "hashtags"],
    "call_to_action": "Optional CTA",
    "confidence_score": 0.0-1.0,
    "cajun_phrases_used": ["phrases", "used"],
    "tone": "warm|casual|celebratory|informative"
}}""",
        expected_output_format="json",
        max_tokens=600,
        temperature=0.7
    )

    STORYTELLING_GENERATOR = PromptTemplate(
        name="storytelling_generator",
        role=PromptRole.GENERATOR,
        system_prompt="""You are a master storyteller for Randol's Restaurant, weaving tales of Louisiana heritage, family traditions, and Cajun culture.

Your stories should:
- Draw from the rich history of Acadiana
- Feature themes of family, tradition, community, and good food
- Use sensory details that make readers taste, smell, and feel Louisiana
- Connect emotionally while remaining authentic to Cajun culture
- Never be longer than 3 short paragraphs for social media""",

        user_template="""Create a storytelling post about: {story_theme}

Story elements to potentially include:
- Family history: {family_context}
- Recipe/dish focus: {dish_focus}
- Cultural reference: {cultural_reference}
- Emotional hook: {emotional_hook}

Platform: {platform}
Target emotion: {target_emotion}

Output as JSON:
{{
    "story_text": "The complete story",
    "opening_hook": "First line that grabs attention",
    "emotional_core": "The heart of the story",
    "call_to_action": "Natural invitation",
    "hashtags": ["relevant", "hashtags"]
}}""",
        expected_output_format="json",
        max_tokens=800,
        temperature=0.8
    )

    # =========================================
    # VALIDATOR PROMPTS
    # =========================================

    BRAND_VOICE_VALIDATOR = PromptTemplate(
        name="brand_voice_validator",
        role=PromptRole.VALIDATOR,
        system_prompt="""You are a brand voice validator for Randol's Restaurant. Your job is to evaluate content for authenticity, brand alignment, and quality.

V.A.U.L.T. Validation Criteria:
1. Voice Authenticity (0-1): Does it sound like genuine Cajun hospitality?
2. Audience Appropriateness (0-1): Is it right for the target platform/audience?
3. Uniqueness (0-1): Does it stand out while staying on-brand?
4. Language Quality (0-1): Are Cajun expressions used naturally, not forced?
5. Tone Alignment (0-1): Is it warm, welcoming, and never salesy?

Red flags to watch for:
- Stereotypical or exaggerated Cajun accents
- Forced or unnatural expressions
- Overly promotional/salesy language
- Culturally insensitive content
- Generic content that could be for any restaurant""",

        user_template="""Validate this content for Randol's brand voice:

Content: {content_text}
Platform: {platform}
Content Type: {content_type}
Intended Audience: {audience}

Evaluate and score each dimension. Be critical but fair.

Output as JSON:
{{
    "scores": {{
        "voice_authenticity": 0.0-1.0,
        "audience_appropriateness": 0.0-1.0,
        "uniqueness": 0.0-1.0,
        "language_quality": 0.0-1.0,
        "tone_alignment": 0.0-1.0
    }},
    "overall_score": 0.0-1.0,
    "approved": true/false,
    "issues_found": ["list", "of", "issues"],
    "improvement_suggestions": ["actionable", "suggestions"],
    "red_flags": ["any", "serious", "concerns"]
}}""",
        expected_output_format="json",
        max_tokens=500,
        temperature=0.3
    )

    CONTENT_QUALITY_VALIDATOR = PromptTemplate(
        name="content_quality_validator",
        role=PromptRole.VALIDATOR,
        system_prompt="""You are a content quality analyst. Evaluate social media content for engagement potential, clarity, and effectiveness.

Quality dimensions:
1. Engagement Potential: Will this make people stop scrolling?
2. Clarity: Is the message clear and easy to understand?
3. Call-to-Action: Is there a natural next step for the reader?
4. Visual Compatibility: Will this work well with images/video?
5. Platform Optimization: Is it optimized for the specific platform?""",

        user_template="""Evaluate content quality:

Content: {content_text}
Platform: {platform}
Character count: {char_count}
Hashtag count: {hashtag_count}
Has media: {has_media}

Output as JSON:
{{
    "quality_scores": {{
        "engagement_potential": 0.0-1.0,
        "clarity": 0.0-1.0,
        "call_to_action_strength": 0.0-1.0,
        "visual_compatibility": 0.0-1.0,
        "platform_optimization": 0.0-1.0
    }},
    "overall_quality": 0.0-1.0,
    "predicted_engagement_rate": "low|medium|high",
    "optimization_suggestions": ["suggestions"]
}}""",
        expected_output_format="json",
        max_tokens=400,
        temperature=0.3
    )

    # =========================================
    # LLM-AS-A-JUDGE PROMPTS
    # =========================================

    AB_TEST_JUDGE = PromptTemplate(
        name="ab_test_judge",
        role=PromptRole.JUDGE,
        system_prompt="""You are an impartial judge comparing two content variants for A/B testing.

Your evaluation must be:
- Objective and based on specific criteria
- Free from position bias (A vs B doesn't matter)
- Focused on predicted real-world performance
- Supported by clear reasoning

Evaluation criteria (in order of importance):
1. Engagement potential - Which will get more interactions?
2. Brand voice alignment - Which better represents Randol's?
3. Emotional resonance - Which connects better emotionally?
4. Clarity and readability - Which is easier to consume?
5. Call-to-action effectiveness - Which drives more action?""",

        user_template="""Compare these two content variants for {platform}:

=== VARIANT A ===
{variant_a}

=== VARIANT B ===
{variant_b}

Context:
- Content type: {content_type}
- Target audience: {target_audience}
- Time of posting: {posting_time}
- Campaign goal: {campaign_goal}

Provide your judgment:

Output as JSON:
{{
    "winner": "A" or "B",
    "confidence": 0.0-1.0,
    "margin": "slight|moderate|significant",
    "reasoning": {{
        "engagement_potential": "Which wins and why",
        "brand_voice": "Which wins and why",
        "emotional_resonance": "Which wins and why",
        "clarity": "Which wins and why",
        "cta_effectiveness": "Which wins and why"
    }},
    "scores": {{
        "variant_a": 0.0-1.0,
        "variant_b": 0.0-1.0
    }},
    "recommendation": "Final recommendation with context"
}}""",
        expected_output_format="json",
        max_tokens=700,
        temperature=0.2
    )

    # =========================================
    # FEEDBACK/IMPROVEMENT PROMPTS
    # =========================================

    CONTENT_IMPROVER = PromptTemplate(
        name="content_improver",
        role=PromptRole.FEEDBACK,
        system_prompt="""You are a content improvement specialist for Randol's Restaurant.
Your job is to take existing content and make it better while preserving the original intent and voice.

Improvement guidelines:
- Enhance Cajun authenticity without overdoing it
- Strengthen emotional connection
- Improve engagement hooks
- Ensure natural flow
- Keep the core message intact""",

        user_template="""Improve this content based on feedback:

Original content:
{original_content}

Validation feedback:
{validation_feedback}

Issues to address:
{issues}

Requirements:
- Keep the same general message
- Address all noted issues
- Maintain or improve authenticity score
- Platform: {platform}

Output as JSON:
{{
    "improved_content": "The improved text",
    "changes_made": ["list", "of", "changes"],
    "issues_addressed": ["which", "issues", "were", "fixed"],
    "remaining_concerns": ["any", "unresolved", "issues"],
    "improvement_confidence": 0.0-1.0
}}""",
        expected_output_format="json",
        max_tokens=600,
        temperature=0.5
    )

    PERFORMANCE_ANALYZER = PromptTemplate(
        name="performance_analyzer",
        role=PromptRole.FEEDBACK,
        system_prompt="""You are a social media performance analyst. Analyze engagement data to provide actionable insights for content optimization.""",

        user_template="""Analyze this content performance data:

Content: {content_text}
Platform: {platform}
Posted: {posted_at}

Metrics:
- Impressions: {impressions}
- Engagements: {engagements}
- Engagement rate: {engagement_rate}
- Shares: {shares}
- Comments: {comments}
- Saves: {saves}

Historical averages for this content type:
- Average engagement rate: {avg_engagement_rate}
- Average shares: {avg_shares}

Output as JSON:
{{
    "performance_rating": "below_average|average|above_average|excellent",
    "key_insights": ["insight1", "insight2"],
    "success_factors": ["what", "worked", "well"],
    "improvement_areas": ["what", "could", "improve"],
    "recommendations_for_future": ["actionable", "recommendations"],
    "optimal_posting_time_suggestion": "time suggestion based on data"
}}""",
        expected_output_format="json",
        max_tokens=500,
        temperature=0.3
    )

    @classmethod
    def get_prompt(cls, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        prompts = {
            "content_generator": cls.CONTENT_GENERATOR,
            "storytelling_generator": cls.STORYTELLING_GENERATOR,
            "brand_voice_validator": cls.BRAND_VOICE_VALIDATOR,
            "content_quality_validator": cls.CONTENT_QUALITY_VALIDATOR,
            "ab_test_judge": cls.AB_TEST_JUDGE,
            "content_improver": cls.CONTENT_IMPROVER,
            "performance_analyzer": cls.PERFORMANCE_ANALYZER
        }
        return prompts.get(name)

    @classmethod
    def list_prompts(cls) -> List[str]:
        """List all available prompt names"""
        return [
            "content_generator",
            "storytelling_generator",
            "brand_voice_validator",
            "content_quality_validator",
            "ab_test_judge",
            "content_improver",
            "performance_analyzer"
        ]


# Platform-specific requirements templates
PLATFORM_REQUIREMENTS = {
    "instagram": {
        "max_chars": 2200,
        "optimal_chars": 125,
        "max_hashtags": 30,
        "optimal_hashtags": 11,
        "requirements": "Use emojis sparingly, focus on visual storytelling, include relevant hashtags"
    },
    "facebook": {
        "max_chars": 63206,
        "optimal_chars": 80,
        "max_hashtags": 3,
        "optimal_hashtags": 1,
        "requirements": "Focus on community engagement, encourage comments, share stories"
    },
    "tiktok": {
        "max_chars": 2200,
        "optimal_chars": 150,
        "max_hashtags": 5,
        "optimal_hashtags": 3,
        "requirements": "Trendy, casual tone, hook in first 3 seconds, use trending sounds reference"
    },
    "twitter": {
        "max_chars": 280,
        "optimal_chars": 100,
        "max_hashtags": 2,
        "optimal_hashtags": 1,
        "requirements": "Concise, punchy, conversational, strong hook"
    },
    "google_posts": {
        "max_chars": 1500,
        "optimal_chars": 300,
        "max_hashtags": 0,
        "optimal_hashtags": 0,
        "requirements": "Professional, informative, include business details, clear CTA"
    }
}


def get_platform_requirements(platform: str) -> Dict[str, Any]:
    """Get platform-specific requirements"""
    return PLATFORM_REQUIREMENTS.get(platform, PLATFORM_REQUIREMENTS["facebook"])
