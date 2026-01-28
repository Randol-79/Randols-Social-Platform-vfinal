"""
Brand Voice Guardian Agent - Ensures authentic Cajun voice and cultural appropriateness
Uses NLP and rule-based validation to maintain brand consistency
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from utils.logger import setup_logger
from utils.cajun_voice import CajunVoiceProcessor

# Try to import TextBlob for sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False


class BrandVoiceGuardianAgent:
    """
    Validates and ensures content maintains authentic Cajun voice.
    Implements the V.A.U.L.T. framework for cultural authenticity.
    """
    
    def __init__(self):
        self.logger = setup_logger("brand_voice_guardian")
        self.cajun_processor = CajunVoiceProcessor()
        self.voice_guidelines = self._load_voice_guidelines()
        self.approved_phrases = self._load_approved_phrases()
        self.flagged_phrases = self._load_flagged_phrases()
        self.authenticity_threshold = 0.75
        self.content_reviewed_today = 0
        self.content_approved_today = 0
        self.status = 'active'
        
    def _load_voice_guidelines(self) -> Dict[str, Any]:
        """Load V.A.U.L.T. framework guidelines"""
        return {
            'voice_foundation': {
                'authentic': True,
                'welcoming': True,
                'proud': True,
                'musical_references': True,
                'family_oriented': True
            },
            'audience_adaptations': {
                'locals': 'casual_cajun_phrases',
                'tourists': 'educational_cultural_context',
                'foodies': 'technical_with_storytelling',
                'families': 'memories_traditions'
            },
            'unique_flavor': {
                'signature_phrases': [
                    "Laissez les bon temps rouler!",
                    "Come see us, cher!",
                    "That's some kinda good!",
                    "Y'all come back now!"
                ],
                'cultural_references': [
                    'crawfish', 'zydeco', 'bayou', 'acadiana',
                    'roux', 'holy trinity', 'boudin', 'étouffée'
                ]
            },
            'tone_requirements': {
                'warm': True,
                'conversational': True,
                'storytelling': True,
                'community_focused': True
            }
        }
        
    def _load_approved_phrases(self) -> List[str]:
        """Load pre-approved Cajun phrases"""
        return [
            "y'all come see us",
            "cher", "chère",
            "that gumbo sings",
            "music to your taste buds",
            "passed down through generations",
            "fresh from local waters",
            "family recipe",
            "authentic louisiana",
            "bon appétit",
            "fais do-do",
            "two-step on over",
            "laissez les bon temps rouler",
            "that's some kinda good",
            "where y'at",
            "come hungry, leave happy"
        ]
        
    def _load_flagged_phrases(self) -> List[str]:
        """Load phrases that should be flagged for review"""
        return [
            "authentic cajun experience",  # too touristy
            "real deal cajun",  # overused
            "y'all come back now ya hear",  # too generic southern
            "southern comfort",  # generic southern
            "down south",  # too general
            "bayou country cooking",  # cliché
            "straight outta the swamp"  # potentially offensive
        ]
    
    async def validate_content(self, content: Dict[str, Any]) -> bool:
        """Main validation function for content"""
        try:
            text = content.get('text', '')
            content_id = content.get('id', 'unknown')
            
            self.content_reviewed_today += 1
            
            # Run all validation checks
            authenticity_score = self.calculate_authenticity_score(text)
            tone_compliance = self._check_tone_compliance(text)
            cultural_appropriateness = self._check_cultural_appropriateness(text)
            brand_consistency = self._check_brand_consistency(text)
            
            validation_results = {
                'content_id': content_id,
                'authenticity_score': authenticity_score,
                'tone_compliance': tone_compliance,
                'cultural_appropriateness': cultural_appropriateness,
                'brand_consistency': brand_consistency
            }
            
            self.logger.info(f"Content validation: {content_id} - Score: {authenticity_score:.2f}")
            
            # Overall approval logic
            is_approved = (
                authenticity_score >= self.authenticity_threshold and
                tone_compliance and
                cultural_appropriateness and
                brand_consistency
            )
            
            if is_approved:
                self.content_approved_today += 1
                self.logger.info(f"Content approved: {content_id}")
            else:
                self.logger.warning(f"Content flagged for review: {content_id}")
                await self._flag_content_for_review(content, validation_results)
            
            return is_approved
            
        except Exception as e:
            self.logger.error(f"Error validating content: {e}")
            return False
    
    def calculate_authenticity_score(self, text: str) -> float:
        """Calculate how authentic the Cajun voice is"""
        score = 0.5  # Base score
        text_lower = text.lower()
        
        # Positive scoring
        
        # Check for approved phrases
        for phrase in self.approved_phrases:
            if phrase.lower() in text_lower:
                score += 0.08
        
        # Check for Louisiana-specific terms
        louisiana_terms = ['louisiana', 'cajun', 'creole', 'bayou', 'gulf', 'zydeco', 
                         'acadiana', 'breaux bridge', 'crawfish', 'étouffée', 'gumbo']
        for term in louisiana_terms:
            if term.lower() in text_lower:
                score += 0.05
        
        # Check for authentic greetings/phrases
        if "y'all" in text_lower:
            score += 0.1
        if "cher" in text_lower:
            score += 0.08
        if any(greeting in text_lower for greeting in ["where y'at", "how's ya mama"]):
            score += 0.05
        
        # Check for storytelling elements
        storytelling_markers = ['family', 'tradition', 'generations', 'recipe', 'heritage', 'grand']
        for marker in storytelling_markers:
            if marker in text_lower:
                score += 0.03
        
        # Negative scoring
        
        # Penalize for flagged phrases
        for phrase in self.flagged_phrases:
            if phrase.lower() in text_lower:
                score -= 0.15
        
        # Check for over-exaggerated dialect
        apostrophe_count = text.count("'")
        word_count = len(text.split())
        if word_count > 0 and (apostrophe_count / word_count) > 0.3:
            score -= 0.2
        
        # Check for offensive stereotypes
        offensive_terms = ['hillbilly', 'redneck', 'backwards', 'swamp people', 'hick']
        for term in offensive_terms:
            if term in text_lower:
                score -= 0.3
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))
    
    def _check_tone_compliance(self, text: str) -> bool:
        """Check if tone matches brand guidelines"""
        text_lower = text.lower()
        
        # Check for warm, welcoming language
        welcoming_words = ['welcome', 'join', 'come', 'visit', 'family', 'home', 
                         'together', 'y\'all', 'cher', 'friends']
        has_welcoming = any(word in text_lower for word in welcoming_words)
        
        # Check for conversational tone (questions, exclamations, personal pronouns)
        conversational_indicators = ['!', '?', 'you', 'your', 'we', 'our', 'us']
        conversational_count = sum(1 for indicator in conversational_indicators if indicator in text)
        has_conversational = conversational_count >= 2
        
        # Check sentiment if TextBlob available
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity
                if sentiment < -0.3:  # Too negative
                    return False
            except:
                pass
        
        return has_welcoming and has_conversational
    
    def _check_cultural_appropriateness(self, text: str) -> bool:
        """Ensure content is culturally appropriate and respectful"""
        text_lower = text.lower()
        
        # Check for offensive stereotypes
        offensive_terms = ['hillbilly', 'redneck', 'backwards', 'primitive', 
                         'hick', 'country bumpkin', 'swamp folk']
        for term in offensive_terms:
            if term in text_lower:
                self.logger.warning(f"Offensive term detected: {term}")
                return False
        
        # Check for over-exaggerated dialect
        apostrophe_count = text.count("'")
        word_count = len(text.split())
        if word_count > 0 and (apostrophe_count / word_count) > 0.35:
            self.logger.warning("Over-exaggerated dialect detected")
            return False
        
        # Check for mocking tone patterns
        mocking_patterns = [r'gonna git', r'fixin\' ta', r'ain\'t got no']
        for pattern in mocking_patterns:
            if re.search(pattern, text_lower):
                self.logger.warning(f"Potentially mocking pattern detected: {pattern}")
                return False
        
        return True
    
    def _check_brand_consistency(self, text: str) -> bool:
        """Check consistency with Randol's brand values"""
        text_lower = text.lower()
        
        brand_values = {
            'family_owned': ['family', 'generations', 'heritage', 'tradition', 'grandm', 'paw paw'],
            'authentic': ['authentic', 'traditional', 'original', 'genuine', 'real'],
            'community': ['community', 'neighbors', 'friends', 'together', 'welcome'],
            'music': ['music', 'live', 'band', 'zydeco', 'dancing', 'dance']
        }
        
        # Should mention at least one brand value
        mentioned_values = 0
        for value_category, keywords in brand_values.items():
            if any(keyword in text_lower for keyword in keywords):
                mentioned_values += 1
        
        # Should avoid corporate/chain language
        corporate_terms = ['franchise', 'corporate', 'brand', 'chain', 'nationwide', 
                         'investors', 'shareholders', 'expansion']
        has_corporate = any(term in text_lower for term in corporate_terms)
        
        if has_corporate:
            self.logger.warning("Corporate language detected")
            return False
        
        return mentioned_values >= 1 or len(text) < 50  # Short posts might not have brand values
    
    async def _flag_content_for_review(self, content: Dict, validation_results: Dict):
        """Flag content that needs human review"""
        flagged_content = {
            'content_id': content.get('id'),
            'original_text': content.get('text'),
            'validation_results': validation_results,
            'flagged_time': datetime.now().isoformat(),
            'status': 'pending_review',
            'recommended_action': self._get_recommended_action(validation_results)
        }
        
        self.logger.warning(f"Content flagged: {content.get('id')} - {flagged_content['recommended_action']}")
        
        # In production, save to database or notification system
        return flagged_content
    
    def _get_recommended_action(self, validation_results: Dict) -> str:
        """Get recommended action for flagged content"""
        score = validation_results.get('authenticity_score', 0)
        
        if score < 0.5:
            return "Enhance Cajun authenticity - add local flavor and cultural references"
        elif not validation_results.get('tone_compliance'):
            return "Adjust tone - make more welcoming and conversational"
        elif not validation_results.get('cultural_appropriateness'):
            return "Review cultural appropriateness - avoid stereotypes or excessive dialect"
        elif not validation_results.get('brand_consistency'):
            return "Improve brand consistency - emphasize family values and authenticity"
        else:
            return "Minor adjustments needed - review and enhance Louisiana voice"
    
    def suggest_improvements(self, text: str) -> List[str]:
        """Suggest specific improvements for content"""
        suggestions = []
        score = self.calculate_authenticity_score(text)
        text_lower = text.lower()
        
        # Authenticity suggestions
        if score < self.authenticity_threshold:
            if "y'all" not in text_lower and "cher" not in text_lower:
                suggestions.append("Add authentic Cajun phrases like 'y'all' or 'cher'")
            
            if not any(term in text_lower for term in ['louisiana', 'cajun', 'bayou', 'acadiana']):
                suggestions.append("Include Louisiana cultural references (bayou, Acadiana, etc.)")
        
        # Tone suggestions
        if not self._check_tone_compliance(text):
            suggestions.append("Make the tone more welcoming and conversational")
            suggestions.append("Add words like 'welcome', 'join us', or 'come see us'")
        
        # Cultural suggestions
        if not self._check_cultural_appropriateness(text):
            suggestions.append("Ensure French phrases have cultural context")
            suggestions.append("Avoid over-exaggerated dialect or stereotypes")
        
        # Brand consistency suggestions
        if not self._check_brand_consistency(text):
            suggestions.append("Emphasize family heritage and authentic traditions")
            suggestions.append("Mention community connection or live music element")
        
        # Storytelling suggestions
        if len(text) > 100 and score < 0.8:
            if not any(word in text_lower for word in ['family', 'tradition', 'generations']):
                suggestions.append("Add storytelling elements about family or traditions")
        
        return suggestions if suggestions else ["Content looks good! Minor polish may help."]
    
    def get_approved_alternatives(self, flagged_phrase: str) -> List[str]:
        """Get approved alternatives for flagged phrases"""
        alternatives = {
            'authentic cajun experience': ['genuine Louisiana traditions', 'real Cajun heritage', 'true Louisiana hospitality'],
            'real deal cajun': ['authentic Louisiana cuisine', 'traditional Cajun cooking', 'genuine Cajun flavor'],
            'southern comfort': ['Louisiana hospitality', 'Cajun warmth', 'Acadiana welcome'],
            'bayou country cooking': ['traditional Louisiana recipes', 'authentic Cajun cuisine', 'family recipes from the bayou'],
            'down south': ['here in Louisiana', 'in Acadiana', 'in Cajun country']
        }
        
        return alternatives.get(flagged_phrase.lower(), ['authentic Louisiana tradition'])
    
    async def batch_validate(self, content_list: List[Dict]) -> List[Dict]:
        """Validate multiple pieces of content"""
        results = []
        for content in content_list:
            is_approved = await self.validate_content(content)
            results.append({
                'content_id': content.get('id'),
                'approved': is_approved,
                'authenticity_score': self.calculate_authenticity_score(content.get('text', '')),
                'suggestions': self.suggest_improvements(content.get('text', ''))
            })
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        approval_rate = (self.content_approved_today / max(self.content_reviewed_today, 1))
        
        return {
            'name': 'Brand Voice Guardian',
            'status': self.status,
            'health': 'good',
            'authenticity_threshold': self.authenticity_threshold,
            'content_reviewed_today': self.content_reviewed_today,
            'content_approved_today': self.content_approved_today,
            'approval_rate': round(approval_rate, 2),
            'flagged_for_review': self.content_reviewed_today - self.content_approved_today,
            'uptime': '99.8%'
        }
    
    async def pause(self):
        """Pause the agent"""
        self.status = 'paused'
        self.logger.info("Brand Voice Guardian paused")
    
    async def resume(self):
        """Resume the agent"""
        self.status = 'active'
        self.logger.info("Brand Voice Guardian resumed")


# Test function
async def test_brand_voice_guardian():
    guardian = BrandVoiceGuardianAgent()
    
    # Test good content
    good_content = {
        'id': 'test_good',
        'text': "Come see us tonight, cher! Fresh crawfish just arrived from Louisiana waters. Laissez les bon temps rouler! 🦞"
    }
    
    # Test bad content
    bad_content = {
        'id': 'test_bad',
        'text': "Visit our franchise location for a corporate dining experience. Expansion nationwide coming soon!"
    }
    
    print("Testing good content:")
    is_approved = await guardian.validate_content(good_content)
    print(f"Approved: {is_approved}")
    print(f"Score: {guardian.calculate_authenticity_score(good_content['text'])}")
    
    print("\nTesting bad content:")
    is_approved = await guardian.validate_content(bad_content)
    print(f"Approved: {is_approved}")
    print(f"Score: {guardian.calculate_authenticity_score(bad_content['text'])}")
    print(f"Suggestions: {guardian.suggest_improvements(bad_content['text'])}")


if __name__ == "__main__":
    asyncio.run(test_brand_voice_guardian())
