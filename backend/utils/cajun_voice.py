"""
Cajun Voice Processor - Handles authentic Louisiana dialect and cultural references
Ensures content maintains proper Cajun authenticity without stereotypes
"""

import re
from typing import Dict, List, Any, Optional
import random
from datetime import datetime

class CajunVoiceProcessor:
    """
    Processes and validates content for authentic Cajun voice.
    Implements the V.A.U.L.T. framework for cultural authenticity.
    """
    
    def __init__(self):
        self.cajun_phrases = self._load_cajun_phrases()
        self.cultural_references = self._load_cultural_references()
        self.voice_patterns = self._load_voice_patterns()
        self.seasonal_terms = self._load_seasonal_terms()
        self.flagged_terms = self._load_flagged_terms()
        
    def _load_cajun_phrases(self) -> Dict[str, List[str]]:
        """Load authentic Cajun phrases by context"""
        return {
            'greetings': [
                "Where y'at?",
                "How's ya mama an' them?",
                "Come see us, cher!",
                "Hey, comment ça va?",
                "Bienvenue!",
                "Good to see y'all!"
            ],
            'expressions': [
                "That's some kinda good!",
                "Mais yeah!",
                "Laissez les bon temps rouler!",
                "C'est si bon!",
                "Bon appétit, y'all!",
                "That gumbo sings!",
                "Music to your taste buds!",
                "Ça c'est bon!",
                "Allons danser!"
            ],
            'invitations': [
                "Y'all come eat with us",
                "Come make yourself at home",
                "Pull up a chair, cher",
                "Come hungry, leave happy",
                "Save room for dessert, cher!",
                "Your table's waiting",
                "The roux is ready!"
            ],
            'food_descriptions': [
                "cooked with love",
                "seasoned just right",
                "made from scratch",
                "family recipe",
                "passed down through generations",
                "fresh from local waters",
                "straight from the bayou",
                "simmered to perfection",
                "that chocolate roux goodness"
            ],
            'closings': [
                "Y'all come back now!",
                "See y'all soon, cher!",
                "Au revoir!",
                "Come back and see us!",
                "Save us a dance!",
                "Don't be a stranger!",
                "À bientôt!"
            ],
            'time_of_day': {
                'morning': [
                    "Rise and shine, y'all!",
                    "Good morning, cher!",
                    "Start your day right!",
                    "Coffee's on!"
                ],
                'afternoon': [
                    "Afternoon, y'all!",
                    "Lunchtime at Randol's!",
                    "Perfect time for étouffee!"
                ],
                'evening': [
                    "Good evening, cher!",
                    "Time for some good music and better food!",
                    "The band's warming up!"
                ]
            }
        }
        
    def _load_cultural_references(self) -> Dict[str, List[str]]:
        """Load Louisiana cultural references"""
        return {
            'music': [
                'zydeco', 'accordion', 'washboard', 'fiddle', 'rubboard',
                'two-step', 'fais do-do', 'Cajun music', 'live band',
                'dance floor', 'Louisiana sound', 'Creole music'
            ],
            'food': [
                'roux', 'holy trinity', 'boudin', 'cracklins', 'boudin balls',
                'étouffee', 'jambalaya', 'gumbo', 'mudbugs', 'crawfish',
                'andouille', 'tasso', 'courtbouillon', 'sauce piquante',
                'dirty rice', 'red beans', 'file', 'okra'
            ],
            'geography': [
                'bayou', 'Gulf Coast', 'Atchafalaya', 'Acadiana',
                'Breaux Bridge', 'swamp', 'marsh', 'Louisiana',
                'Vermilion Parish', 'St. Martin Parish', 'Teche country'
            ],
            'culture': [
                'Mardi Gras', 'Acadian', 'Creole', 'heritage',
                'tradition', 'joie de vivre', 'community', 'family',
                'generations', 'Grand-mère', 'Paw Paw', 'Cajun pride'
            ],
            'seasons': [
                'crawfish season', 'carnival season', 'festival season',
                'shrimp season', 'oyster season', 'Festivals Acadiens',
                'Breaux Bridge Crawfish Festival'
            ]
        }
        
    def _load_voice_patterns(self) -> Dict[str, Any]:
        """Load authentic voice patterns and grammar"""
        return {
            'contractions': {
                'you all': "y'all",
                'going to': "gonna",
                'want to': "wanna",
                'kind of': "kinda",
                'sort of': "sorta"
            },
            'sentence_starters': [
                "Let me tell you,",
                "I'm gonna tell you what,",
                "Listen here, cher,",
                "You know what?",
                "Mais, let me tell you,",
                "Now, I tell you,"
            ],
            'emphasis_words': [
                "mais", "cher", "sha", "bébé"
            ],
            'storytelling_phrases': [
                "Back in the day,",
                "My Grand-mère always said,",
                "For generations,",
                "In our family,",
                "The old folks taught us,"
            ]
        }
        
    def _load_seasonal_terms(self) -> Dict[str, List[str]]:
        """Load seasonal vocabulary"""
        return {
            'spring': [
                'crawfish season', 'mudbugs', 'boil', 'fresh catch',
                'springtime on the bayou', 'crawfish are running'
            ],
            'summer': [
                'festival season', 'outdoor dining', 'live music under the stars',
                'dancing', 'summer nights', 'Gulf shrimp'
            ],
            'fall': [
                'harvest', 'comfort food', 'gumbo weather', 'family time',
                'cooler nights', 'football season', 'hunting season'
            ],
            'winter': [
                'warm hearts', 'hot gumbo', 'cozy atmosphere', 'comfort',
                'holiday traditions', 'family gatherings'
            ],
            'mardi_gras': [
                'carnival', 'celebration', 'king cake', 'parades',
                'beads', 'masks', 'laissez les bon temps rouler',
                'Fat Tuesday', 'Mardi Gras mambo'
            ]
        }
        
    def _load_flagged_terms(self) -> List[str]:
        """Load terms that should be avoided"""
        return [
            'hillbilly', 'redneck', 'backwards', 'primitive',
            'hick', 'country bumpkin', 'swamp people', 'swamp folk',
            'simple folk', 'backwoods', 'boonies'
        ]
    
    def get_system_prompt(self) -> str:
        """Get system prompt for AI content generation"""
        return """
You are a content creator for Randol's Restaurant in Breaux Bridge, Louisiana - the "Crawfish Capital of the World."

VOICE GUIDELINES (V.A.U.L.T. Framework):

VOICE FOUNDATION:
- Authentic Louisiana Cajun hospitality - warm, welcoming, genuine
- Like inviting someone into your family home
- Proud of heritage without being boastful
- Musical soul - references to zydeco, live music, dancing naturally woven in
- Family-oriented - emphasize traditions, generations, community

AUDIENCE RESONANCE:
- Local Regulars: Casual, familiar tone with insider references
- Louisiana Tourists: Educational context with cultural background
- Food Enthusiasts: Technical details balanced with storytelling
- Families: Emphasis on memories, traditions, multi-generational dining

UNIQUE LOUISIANA FLAVOR:
- Natural use of "y'all" for groups
- "Cher" as term of endearment (pronounced 'sha') - use sparingly
- Reference Louisiana culture authentically (zydeco, crawfish, bayou, Acadiana)
- Storytelling that connects food to family history
- Musical metaphors: "That gumbo sings!", "Music to your taste buds!"

LANGUAGE DO's:
- Warm, conversational tone
- Natural Cajun expressions that flow
- Cultural references that educate while welcoming
- Community-focused messaging
- Proudly local but never exclusive

LANGUAGE DON'Ts:
- Over-exaggerated dialect or caricatures
- Generic Southern phrases not specific to Louisiana
- Corporate or chain restaurant language
- Stereotypical portrayals that mock the culture
- Excessive use of apostrophes or phonetic spelling

TONE SPECTRUM:
- Casual Local: "Where y'at? Come eat some boudin, cher!"
- Welcoming Tourist: "Welcome to authentic Louisiana! Let us share our family's gumbo recipe..."
- Educational: "Did you know crawfish season peaks in spring? Here's why..."
- Celebratory: "Laissez les bon temps rouler! Live zydeco music tonight!"

Remember: You're representing 50+ years of family tradition and the rich Cajun culture of Louisiana. Every word should feel like it's coming from someone who truly loves and lives this culture.
"""
    
    def enhance_cajun_authenticity(self, text: str, context: Optional[str] = None) -> str:
        """Enhance text with authentic Cajun elements"""
        enhanced_text = text
        
        # Apply natural contractions
        for original, cajun in self.voice_patterns['contractions'].items():
            enhanced_text = re.sub(
                rf'\b{original}\b',
                cajun,
                enhanced_text,
                flags=re.IGNORECASE
            )
        
        # Add cultural reference if none exists and text is long enough
        if not self._has_cultural_references(enhanced_text) and len(enhanced_text) > 100:
            enhanced_text = self._add_cultural_touch(enhanced_text, context)
        
        # Ensure warm closing if not present
        if not self._has_warm_closing(enhanced_text):
            closing = random.choice(self.cajun_phrases['closings'])
            enhanced_text = f"{enhanced_text.rstrip('.')} {closing}"
        
        return enhanced_text
    
    def _has_cultural_references(self, text: str) -> bool:
        """Check if text contains cultural references"""
        text_lower = text.lower()
        for category, references in self.cultural_references.items():
            if any(ref.lower() in text_lower for ref in references):
                return True
        return False
    
    def _has_warm_closing(self, text: str) -> bool:
        """Check if text has a warm, inviting closing"""
        text_lower = text.lower()
        closing_indicators = [
            'come', 'visit', 'see y\'all', 'cher', 'y\'all come',
            'welcome', 'join us', 'save', 'waiting'
        ]
        return any(indicator in text_lower for indicator in closing_indicators)
    
    def _add_cultural_touch(self, text: str, context: Optional[str] = None) -> str:
        """Add a subtle cultural touch to text"""
        # Determine appropriate category based on context
        if context:
            if 'food' in context.lower():
                category = 'food'
            elif 'music' in context.lower() or 'event' in context.lower():
                category = 'music'
            else:
                category = random.choice(['culture', 'geography'])
        else:
            category = random.choice(list(self.cultural_references.keys()))
        
        reference = random.choice(self.cultural_references[category])
        
        # Add naturally at the end
        sentences = text.split('. ')
        if len(sentences) > 1:
            connector_phrases = [
                f"It's all part of our {reference} tradition.",
                f"That's the {reference} way.",
                f"Just how we do it here in Louisiana."
            ]
            sentences.append(random.choice(connector_phrases))
            return '. '.join(sentences)
        
        return text
    
    def get_contextual_phrases(self, context: str) -> List[str]:
        """Get contextually appropriate phrases"""
        context_lower = context.lower()
        
        if 'morning' in context_lower:
            return self.cajun_phrases['time_of_day']['morning']
        elif 'afternoon' in context_lower or 'lunch' in context_lower:
            return self.cajun_phrases['time_of_day']['afternoon']
        elif 'evening' in context_lower or 'dinner' in context_lower:
            return self.cajun_phrases['time_of_day']['evening']
        elif 'food' in context_lower or 'special' in context_lower:
            return self.cajun_phrases['food_descriptions'] + self.cajun_phrases['expressions']
        elif 'invitation' in context_lower or 'welcome' in context_lower:
            return self.cajun_phrases['invitations']
        elif 'greeting' in context_lower:
            return self.cajun_phrases['greetings']
        else:
            return self.cajun_phrases['expressions']
    
    def get_seasonal_vocabulary(self) -> Dict[str, Any]:
        """Get current seasonal vocabulary"""
        month = datetime.now().month
        
        if month in [2, 3]:  # Mardi Gras season (Feb-March)
            return {
                'season': 'mardi_gras',
                'terms': self.seasonal_terms['mardi_gras'],
                'content_boost': 2.0
            }
        elif month in [3, 4, 5, 6]:  # Spring/Crawfish season
            return {
                'season': 'crawfish_season',
                'terms': self.seasonal_terms['spring'],
                'content_boost': 1.5
            }
        elif month in [6, 7, 8]:  # Summer
            return {
                'season': 'festival_season',
                'terms': self.seasonal_terms['summer'],
                'content_boost': 1.3
            }
        elif month in [9, 10, 11]:  # Fall
            return {
                'season': 'fall',
                'terms': self.seasonal_terms['fall'],
                'content_boost': 1.2
            }
        else:  # Winter
            return {
                'season': 'winter',
                'terms': self.seasonal_terms['winter'],
                'content_boost': 1.1
            }
    
    def validate_authenticity(self, text: str) -> Dict[str, Any]:
        """Validate text for authentic Cajun voice"""
        score = 0.5  # Base score
        issues = []
        text_lower = text.lower()
        
        # Positive scoring
        
        # Check for authentic phrases
        authentic_phrases = ["y'all", "cher", "laissez", "bon temps", "mais"]
        for phrase in authentic_phrases:
            if phrase in text_lower:
                score += 0.08
        
        # Check for cultural references
        if self._has_cultural_references(text):
            score += 0.15
        
        # Check for storytelling elements
        storytelling_markers = ['family', 'tradition', 'generations', 'recipe', 'heritage']
        storytelling_count = sum(1 for marker in storytelling_markers if marker in text_lower)
        score += (storytelling_count * 0.05)
        
        # Check for warm tone
        warm_words = ['welcome', 'home', 'love', 'share', 'together', 'friends', 'neighbors']
        warm_count = sum(1 for word in warm_words if word in text_lower)
        score += (warm_count * 0.03)
        
        # Negative scoring
        
        # Check for flagged/offensive terms
        for term in self.flagged_terms:
            if term in text_lower:
                score -= 0.3
                issues.append(f'Contains potentially offensive term: "{term}"')
        
        # Check for over-exaggerated dialect
        apostrophe_ratio = text.count("'") / max(len(text.split()), 1)
        if apostrophe_ratio > 0.3:
            score -= 0.2
            issues.append('Over-exaggerated dialect (too many apostrophes)')
        
        # Check for generic Southern (non-Louisiana) phrases
        generic_southern = ['fixin to', 'y\'all come back now ya hear', 'bless your heart']
        for phrase in generic_southern:
            if phrase in text_lower:
                score -= 0.1
                issues.append(f'Generic Southern phrase (not Louisiana-specific): "{phrase}"')
        
        # Check for corporate language
        corporate_terms = ['franchise', 'brand', 'corporate', 'chain', 'nationwide']
        for term in corporate_terms:
            if term in text_lower:
                score -= 0.15
                issues.append(f'Corporate language detected: "{term}"')
        
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        return {
            'authenticity_score': round(score, 3),
            'issues': issues,
            'recommendations': self._get_improvement_recommendations(score, issues),
            'passed': score >= 0.75
        }
    
    def _get_improvement_recommendations(self, score: float, issues: List[str]) -> List[str]:
        """Get recommendations for improving authenticity"""
        recommendations = []
        
        if score < 0.6:
            recommendations.append("Add authentic Cajun phrases like 'cher' or 'Laissez les bon temps rouler!'")
            recommendations.append("Include Louisiana cultural references (zydeco, bayou, Acadiana)")
        
        if score < 0.75:
            recommendations.append("Add storytelling elements about family traditions or recipes")
            recommendations.append("Include warm, welcoming language that invites community")
        
        if 'over-exaggerated' in ' '.join(issues).lower():
            recommendations.append("Reduce excessive apostrophes - keep dialect natural, not cartoonish")
        
        if 'offensive' in ' '.join(issues).lower():
            recommendations.append("Remove stereotypical terms - focus on genuine cultural pride")
        
        if 'corporate' in ' '.join(issues).lower():
            recommendations.append("Replace corporate language with family-focused messaging")
        
        return recommendations
    
    def generate_hashtags(self, base_keywords: List[str], platform: str = 'instagram') -> List[str]:
        """Generate Louisiana-specific hashtags"""
        # Base hashtags always included
        base_tags = [
            '#RandolsRestaurant', '#BreauxBridge', '#CajunFood', '#Louisiana',
            '#AuthenticCajun', '#Acadiana'
        ]
        
        # Keyword-specific tags
        keyword_tags = []
        for keyword in base_keywords:
            keyword_lower = keyword.lower()
            
            if keyword_lower in ['crawfish', 'mudbugs', 'crawfish boil']:
                keyword_tags.extend([
                    '#CrawfishBoil', '#Mudbugs', '#LouisianaCrawfish',
                    '#CrawfishSeason', '#CrawfishCapital'
                ])
            elif keyword_lower in ['music', 'zydeco', 'live music']:
                keyword_tags.extend([
                    '#ZydecoMusic', '#LiveMusic', '#CajunMusic',
                    '#DancingInLouisiana', '#FaisDoDo'
                ])
            elif keyword_lower in ['gumbo', 'jambalaya', 'etouffee']:
                keyword_tags.extend([
                    '#CajunCooking', '#CreoleFood', '#LouisianaKitchen',
                    '#SoulFood', '#ComfortFood'
                ])
            elif keyword_lower in ['family', 'tradition']:
                keyword_tags.extend([
                    '#FamilyTradition', '#CajunHeritage', '#LouisianaProud'
                ])
        
        # Seasonal tags
        seasonal = self.get_seasonal_vocabulary()
        if seasonal['season'] == 'mardi_gras':
            keyword_tags.extend(['#MardiGras', '#Carnival', '#LaissezLesBonTempsRouler'])
        elif seasonal['season'] == 'crawfish_season':
            keyword_tags.extend(['#CrawfishSeason', '#SpringInLouisiana'])
        
        # Combine and deduplicate
        all_tags = list(dict.fromkeys(base_tags + keyword_tags))
        
        # Platform-specific limits
        limits = {'instagram': 30, 'facebook': 10, 'tiktok': 20, 'youtube': 15}
        limit = limits.get(platform, 30)
        
        return all_tags[:limit]
    
    def get_random_phrase(self, category: str = 'expressions') -> str:
        """Get a random phrase from a category"""
        if category in self.cajun_phrases:
            return random.choice(self.cajun_phrases[category])
        return random.choice(self.cajun_phrases['expressions'])
    
    def get_storytelling_opener(self) -> str:
        """Get a storytelling opening phrase"""
        return random.choice(self.voice_patterns['storytelling_phrases'])


# Singleton instance
cajun_voice = CajunVoiceProcessor()
