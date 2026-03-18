"""
Clazzy V2 - AI Assistant Layer
Natural language interface using LLM (Claude/OpenAI) for intent parsing
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
import logging

logger = logging.getLogger(__name__)

# Optional imports
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class IntentType(str, Enum):
    """Types of user intents"""
    OUTFIT_RECOMMENDATION = "outfit_recommendation"
    MATCH_ITEM = "match_item"
    WARDROBE_QUERY = "wardrobe_query"
    STYLE_ADVICE = "style_advice"
    COLOR_ADVICE = "color_advice"
    OCCASION_OUTFIT = "occasion_outfit"
    WEATHER_APPROPRIATE = "weather_appropriate"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """Structured representation of user intent"""
    intent_type: IntentType
    confidence: float
    occasion: Optional[str] = None
    target_item: Optional[str] = None
    color_preference: Optional[str] = None
    style_preference: Optional[str] = None
    weather: Optional[str] = None
    time_of_day: Optional[str] = None
    constraints: List[str] = None
    original_query: str = ""

    def to_dict(self) -> Dict:
        return {
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
            "occasion": self.occasion,
            "target_item": self.target_item,
            "color_preference": self.color_preference,
            "style_preference": self.style_preference,
            "weather": self.weather,
            "time_of_day": self.time_of_day,
            "constraints": self.constraints or [],
            "original_query": self.original_query
        }


class RuleBasedIntentParser:
    """
    Fast rule-based intent parser for common queries
    Falls back to LLM for complex cases
    """

    OCCASION_KEYWORDS = {
        "date": ["date", "romantic", "dinner", "anniversary"],
        "formal": ["formal", "business", "meeting", "presentation", "interview"],
        "office": ["office", "work", "professional", "corporate"],
        "party": ["party", "celebration", "night out", "club"],
        "casual": ["casual", "relaxed", "everyday", "chill", "hanging out"],
        "wedding": ["wedding", "ceremony", "reception"],
        "workout": ["workout", "gym", "exercise", "running", "yoga"],
        "beach": ["beach", "pool", "vacation", "summer"],
        "college": ["college", "class", "university", "school"]
    }

    WEATHER_KEYWORDS = {
        "hot": ["hot", "warm", "summer", "heat", "sunny"],
        "cold": ["cold", "winter", "freezing", "snow", "chilly"],
        "rainy": ["rain", "rainy", "wet", "monsoon"],
        "mild": ["spring", "fall", "autumn", "cool", "mild"]
    }

    STYLE_KEYWORDS = {
        "casual": ["casual", "relaxed", "comfortable", "laid-back"],
        "formal": ["formal", "elegant", "sophisticated", "classy"],
        "streetwear": ["streetwear", "urban", "street style", "trendy"],
        "minimalist": ["minimalist", "simple", "clean", "basic"],
        "bohemian": ["boho", "bohemian", "free-spirited", "artistic"],
        "preppy": ["preppy", "classic", "collegiate"],
        "athletic": ["athletic", "sporty", "athleisure"],
        "vintage": ["vintage", "retro", "classic", "old-school"]
    }

    def parse(self, query: str) -> ParsedIntent:
        """Parse user query using rule-based approach"""
        query_lower = query.lower()

        # Detect intent type
        intent_type, confidence = self._detect_intent_type(query_lower)

        # Extract entities
        occasion = self._extract_occasion(query_lower)
        weather = self._extract_weather(query_lower)
        style = self._extract_style(query_lower)
        color = self._extract_color(query_lower)
        target_item = self._extract_target_item(query_lower)
        time_of_day = self._extract_time(query_lower)

        return ParsedIntent(
            intent_type=intent_type,
            confidence=confidence,
            occasion=occasion,
            target_item=target_item,
            color_preference=color,
            style_preference=style,
            weather=weather,
            time_of_day=time_of_day,
            original_query=query
        )

    def _detect_intent_type(self, query: str) -> Tuple[IntentType, float]:
        """Detect the type of user intent"""
        # Match item patterns
        if any(p in query for p in ["match this", "go with", "pair with", "match my"]):
            return IntentType.MATCH_ITEM, 0.9

        # Outfit recommendation patterns
        if any(p in query for p in ["what should i wear", "outfit for", "suggest outfit",
                                     "recommend outfit", "help me dress", "what to wear"]):
            return IntentType.OUTFIT_RECOMMENDATION, 0.9

        # Occasion-specific patterns
        if any(kw in query for kws in self.OCCASION_KEYWORDS.values() for kw in kws):
            return IntentType.OCCASION_OUTFIT, 0.85

        # Weather patterns
        if any(p in query for p in ["rainy day", "hot weather", "cold weather", "summer outfit"]):
            return IntentType.WEATHER_APPROPRIATE, 0.85

        # Color advice
        if any(p in query for p in ["what colors", "color combination", "which color"]):
            return IntentType.COLOR_ADVICE, 0.8

        # Style advice
        if any(p in query for p in ["style tips", "how to style", "fashion advice"]):
            return IntentType.STYLE_ADVICE, 0.8

        # Wardrobe queries
        if any(p in query for p in ["in my wardrobe", "do i have", "what do i have"]):
            return IntentType.WARDROBE_QUERY, 0.8

        return IntentType.UNKNOWN, 0.5

    def _extract_occasion(self, query: str) -> Optional[str]:
        """Extract occasion from query"""
        for occasion, keywords in self.OCCASION_KEYWORDS.items():
            if any(kw in query for kw in keywords):
                return occasion
        return None

    def _extract_weather(self, query: str) -> Optional[str]:
        """Extract weather context from query"""
        for weather, keywords in self.WEATHER_KEYWORDS.items():
            if any(kw in query for kw in keywords):
                return weather
        return None

    def _extract_style(self, query: str) -> Optional[str]:
        """Extract style preference from query"""
        for style, keywords in self.STYLE_KEYWORDS.items():
            if any(kw in query for kw in keywords):
                return style
        return None

    def _extract_color(self, query: str) -> Optional[str]:
        """Extract color preference from query"""
        colors = ["black", "white", "navy", "blue", "red", "green", "brown",
                  "gray", "grey", "beige", "pink", "purple", "yellow", "orange"]
        for color in colors:
            if color in query:
                return color
        return None

    def _extract_target_item(self, query: str) -> Optional[str]:
        """Extract target clothing item from query"""
        # Match patterns like "match this X", "my X shirt"
        items = ["shirt", "t-shirt", "jeans", "pants", "trousers", "blazer",
                 "jacket", "dress", "skirt", "shoes", "hoodie", "sweater"]

        for item in items:
            if item in query:
                # Try to extract color + item
                color_match = self._extract_color(query)
                if color_match:
                    return f"{color_match} {item}"
                return item
        return None

    def _extract_time(self, query: str) -> Optional[str]:
        """Extract time of day from query"""
        times = {
            "morning": ["morning", "breakfast", "brunch"],
            "afternoon": ["afternoon", "lunch", "midday"],
            "evening": ["evening", "dinner", "night", "nighttime"]
        }
        for time, keywords in times.items():
            if any(kw in query for kw in keywords):
                return time
        return None


class LLMIntentParser:
    """
    LLM-powered intent parser for complex queries
    Uses Claude or OpenAI for natural language understanding
    """

    SYSTEM_PROMPT = """You are a fashion assistant intent parser. Given a user query about fashion or outfits,
extract the following information in JSON format:

{
    "intent_type": one of ["outfit_recommendation", "match_item", "wardrobe_query", "style_advice", "color_advice", "occasion_outfit", "weather_appropriate", "general_question"],
    "confidence": float between 0 and 1,
    "occasion": string or null (e.g., "date", "office", "party", "casual", "wedding"),
    "target_item": string or null (the item user wants to match, e.g., "black shirt"),
    "color_preference": string or null,
    "style_preference": string or null (e.g., "casual", "formal", "minimalist"),
    "weather": string or null (e.g., "hot", "cold", "rainy"),
    "time_of_day": string or null (e.g., "morning", "evening"),
    "constraints": list of strings (any restrictions mentioned)
}

Be precise and only include information explicitly or strongly implied in the query.
Return ONLY valid JSON, no other text."""

    def __init__(
        self,
        provider: str = "anthropic",  # "anthropic" or "openai"
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.provider = provider

        if provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed")
            self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
            self.model = model or "claude-sonnet-4-20250514"
        elif provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed")
            self.client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
            self.model = model or "gpt-4o-mini"
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def parse(self, query: str) -> ParsedIntent:
        """Parse user query using LLM"""
        try:
            if self.provider == "anthropic":
                response = self._parse_anthropic(query)
            else:
                response = self._parse_openai(query)

            return self._response_to_intent(response, query)

        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            # Fallback to rule-based
            fallback = RuleBasedIntentParser()
            return fallback.parse(query)

    def _parse_anthropic(self, query: str) -> Dict:
        """Parse using Claude"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Parse this fashion query: {query}"}
            ]
        )

        # Extract JSON from response
        content = message.content[0].text
        return json.loads(content)

    def _parse_openai(self, query: str) -> Dict:
        """Parse using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Parse this fashion query: {query}"}
            ],
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        return json.loads(content)

    def _response_to_intent(self, response: Dict, original_query: str) -> ParsedIntent:
        """Convert LLM response to ParsedIntent"""
        intent_type_str = response.get("intent_type", "unknown")
        try:
            intent_type = IntentType(intent_type_str)
        except ValueError:
            intent_type = IntentType.UNKNOWN

        return ParsedIntent(
            intent_type=intent_type,
            confidence=response.get("confidence", 0.8),
            occasion=response.get("occasion"),
            target_item=response.get("target_item"),
            color_preference=response.get("color_preference"),
            style_preference=response.get("style_preference"),
            weather=response.get("weather"),
            time_of_day=response.get("time_of_day"),
            constraints=response.get("constraints", []),
            original_query=original_query
        )


class ResponseGenerator:
    """
    Generates natural language responses for outfit recommendations
    """

    RESPONSE_TEMPLATES = {
        IntentType.OUTFIT_RECOMMENDATION: [
            "Here are some outfit suggestions for you:",
            "Based on your preferences, I recommend:",
            "I've put together these outfits for you:"
        ],
        IntentType.MATCH_ITEM: [
            "Here's what goes well with {item}:",
            "Great choice! Pair {item} with:",
            "{item} would look great with:"
        ],
        IntentType.OCCASION_OUTFIT: [
            "For your {occasion}, I suggest:",
            "Perfect outfits for {occasion}:",
            "Here's what to wear to {occasion}:"
        ]
    }

    def __init__(
        self,
        use_llm: bool = False,
        llm_provider: str = "anthropic",
        api_key: Optional[str] = None
    ):
        self.use_llm = use_llm
        if use_llm:
            self.llm_parser = LLMIntentParser(llm_provider, api_key)

    def generate_response(
        self,
        intent: ParsedIntent,
        recommendations: List[Dict],
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate response with outfit recommendations

        Args:
            intent: Parsed user intent
            recommendations: List of outfit recommendations
            context: Additional context (weather, user profile, etc.)

        Returns:
            Formatted response with recommendations
        """
        # Build intro text
        intro = self._build_intro(intent)

        # Format outfit cards
        outfit_cards = []
        for i, rec in enumerate(recommendations[:5]):
            card = self._format_outfit_card(rec, i + 1)
            outfit_cards.append(card)

        # Build tips if any
        tips = self._build_tips(intent, context)

        return {
            "intro": intro,
            "outfits": outfit_cards,
            "tips": tips,
            "query_understanding": intent.to_dict()
        }

    def _build_intro(self, intent: ParsedIntent) -> str:
        """Build introduction text"""
        templates = self.RESPONSE_TEMPLATES.get(
            intent.intent_type,
            ["Here are my suggestions:"]
        )

        template = templates[0]

        # Fill placeholders
        if intent.target_item:
            template = template.replace("{item}", intent.target_item)
        if intent.occasion:
            template = template.replace("{occasion}", intent.occasion)

        return template

    def _format_outfit_card(self, recommendation: Dict, rank: int) -> Dict:
        """Format a single outfit recommendation"""
        items = recommendation.get("items", [])
        score = recommendation.get("score", 0)
        reasons = recommendation.get("reasons", [])

        return {
            "rank": rank,
            "items": [
                {
                    "type": item.get("clothing_type"),
                    "color": item.get("colors", [{}])[0].get("name", "Unknown"),
                    "image": item.get("image_path")
                }
                for item in items
            ],
            "score": round(score * 100),
            "match_quality": self._score_to_quality(score),
            "reasons": reasons[:3]
        }

    def _score_to_quality(self, score: float) -> str:
        """Convert score to quality label"""
        if score >= 0.85:
            return "Excellent Match"
        elif score >= 0.7:
            return "Great Match"
        elif score >= 0.55:
            return "Good Match"
        else:
            return "Okay Match"

    def _build_tips(
        self,
        intent: ParsedIntent,
        context: Optional[Dict]
    ) -> List[str]:
        """Build contextual tips"""
        tips = []

        if intent.occasion == "interview":
            tips.append("Keep it professional with neutral colors")

        if intent.weather == "hot":
            tips.append("Choose breathable fabrics like cotton or linen")
        elif intent.weather == "cold":
            tips.append("Layer up for warmth and style")

        if context and context.get("weather_forecast"):
            forecast = context["weather_forecast"]
            if forecast.get("rain_probability", 0) > 50:
                tips.append("Consider taking an umbrella - rain expected")

        return tips


class FashionAssistant:
    """
    Main AI assistant orchestrator
    Handles the full flow from query to recommendation
    """

    def __init__(
        self,
        recommendation_engine,
        personalization_engine=None,
        use_llm: bool = True,
        llm_provider: str = "anthropic",
        api_key: Optional[str] = None
    ):
        self.recommendation_engine = recommendation_engine
        self.personalization_engine = personalization_engine

        # Intent parsing - try LLM first, fallback to rules
        self.rule_parser = RuleBasedIntentParser()
        self.llm_parser = None
        if use_llm and (ANTHROPIC_AVAILABLE or OPENAI_AVAILABLE):
            try:
                self.llm_parser = LLMIntentParser(llm_provider, api_key)
            except Exception as e:
                logger.warning(f"LLM parser init failed: {e}")

        self.response_generator = ResponseGenerator(use_llm, llm_provider, api_key)

    def process_query(
        self,
        query: str,
        user_id: str,
        wardrobe: List[Dict],
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process a natural language query and return recommendations

        Args:
            query: User's natural language query
            user_id: User ID for personalization
            wardrobe: User's wardrobe items
            context: Additional context (location, time, weather)

        Returns:
            Complete response with recommendations
        """
        # Parse intent
        intent = self._parse_intent(query)
        logger.info(f"Parsed intent: {intent.intent_type} (conf: {intent.confidence})")

        # Get user preferences
        user_prefs = None
        if self.personalization_engine:
            user_prefs = self.personalization_engine.get_recommendation_context(user_id)

        # Determine occasion
        occasion = intent.occasion or "casual"

        # Handle specific intent types
        if intent.intent_type == IntentType.MATCH_ITEM and intent.target_item:
            recommendations = self._handle_match_item(
                intent.target_item, wardrobe, occasion, user_prefs
            )
        else:
            # Generate outfit recommendations
            recommendations = self._generate_recommendations(
                wardrobe, occasion, user_prefs, intent
            )

        # Generate response
        response = self.response_generator.generate_response(
            intent, recommendations, context
        )

        return response

    def _parse_intent(self, query: str) -> ParsedIntent:
        """Parse query intent, LLM with rule fallback"""
        # First try rule-based (fast)
        rule_intent = self.rule_parser.parse(query)

        # If confidence is high or no LLM, use rule-based
        if rule_intent.confidence >= 0.85 or not self.llm_parser:
            return rule_intent

        # Try LLM for complex queries
        try:
            llm_intent = self.llm_parser.parse(query)
            return llm_intent
        except Exception:
            return rule_intent

    def _handle_match_item(
        self,
        target_item: str,
        wardrobe: List[Dict],
        occasion: str,
        user_prefs: Optional[Dict]
    ) -> List[Dict]:
        """Handle 'match this item' queries"""
        # Find the target item in wardrobe
        target = None
        for item in wardrobe:
            if target_item.lower() in item.get("name", "").lower():
                target = item
                break

        if not target:
            # Item not in wardrobe - generate generic recommendations
            return self.recommendation_engine.generate_outfits(
                wardrobe, occasion, user_prefs, top_k=5
            )

        # Generate outfits that include this item
        return self.recommendation_engine.generate_outfits(
            wardrobe, occasion, user_prefs, top_k=5, must_include=target
        )

    def _generate_recommendations(
        self,
        wardrobe: List[Dict],
        occasion: str,
        user_prefs: Optional[Dict],
        intent: ParsedIntent
    ) -> List[Dict]:
        """Generate outfit recommendations based on parsed intent"""
        # Apply style filter from intent
        style_filter = intent.style_preference
        if style_filter and user_prefs:
            user_prefs = {**user_prefs, "styles": [style_filter]}

        # Generate recommendations
        recommendations = self.recommendation_engine.generate_outfits(
            wardrobe, occasion, user_prefs, top_k=5
        )

        # Apply personalization re-ranking if available
        if self.personalization_engine:
            recommendations = self.personalization_engine.personalize_recommendations(
                wardrobe[0].get("user_id", "anonymous") if wardrobe else "anonymous",
                recommendations
            )

        return recommendations
