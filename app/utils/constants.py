"""
Application-wide constants for the Monsoon Preparedness platform.

Centralizes magic numbers, default values, and configuration
constants to prevent duplication and improve maintainability.
"""

# --------------------------------------------------------------------------- #
#  Supported Languages
# --------------------------------------------------------------------------- #
LANGUAGE_MAP: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "kn": "Kannada",
}

# --------------------------------------------------------------------------- #
#  Validation Constraints
# --------------------------------------------------------------------------- #
MAX_LOCATION_LENGTH: int = 100
MAX_TEXT_INPUT_LENGTH: int = 500
MIN_FAMILY_SIZE: int = 1
MAX_FAMILY_SIZE: int = 50
ALLOWED_LOCATION_PATTERN: str = r"^[a-zA-Z\s\-,\.]+$"

# --------------------------------------------------------------------------- #
#  Monsoon Risk Levels
# --------------------------------------------------------------------------- #
RISK_LEVELS: dict[str, dict[str, str]] = {
    "low": {
        "label": "Low",
        "color": "#4ade80",
        "description": "Normal conditions. Stay prepared.",
    },
    "moderate": {
        "label": "Moderate",
        "color": "#fbbf24",
        "description": "Rainfall expected. Review your checklist.",
    },
    "high": {
        "label": "High",
        "color": "#f97316",
        "description": "Heavy rainfall warning. Avoid travel.",
    },
    "severe": {
        "label": "Severe",
        "color": "#ef4444",
        "description": "Extreme weather alert. Seek shelter immediately.",
    },
}

# --------------------------------------------------------------------------- #
#  Cache Defaults
# --------------------------------------------------------------------------- #
DEFAULT_CACHE_TTL_SECONDS: int = 300
DEFAULT_CACHE_MAX_SIZE: int = 128

# --------------------------------------------------------------------------- #
#  GenAI Prompt Templates
# --------------------------------------------------------------------------- #
PREPAREDNESS_PLAN_PROMPT: str = """
You are a monsoon safety expert assistant. Generate a personalized monsoon
preparedness plan for a family based on the following details:

- Location: {location}
- Family Size: {family_size}
- Special Needs: {special_needs}
- Language: {language}

Provide the plan in {language_name} language. Structure the response as a
JSON object with the following keys:
- "title": A descriptive title for the plan
- "risk_level": One of "low", "moderate", "high", "severe"
- "sections": An array of objects, each with "heading" and "items" (array of strings)
- "emergency_contacts": An array of relevant emergency numbers

Focus on practical, actionable advice specific to monsoon conditions in the
given location. Include guidance on water safety, electrical safety, food
storage, evacuation routes, and medical preparedness.
"""

CHECKLIST_PROMPT: str = """
You are a monsoon emergency preparedness specialist. Generate a comprehensive
emergency checklist for monsoon season based on:

- Location: {location}
- Family Size: {family_size}
- Special Needs: {special_needs}
- Language: {language}

Respond in {language_name} language. Structure as a JSON object with:
- "title": Checklist title
- "categories": Array of objects with "name" and "items" (each item has "task", "priority": "high"/"medium"/"low", "completed": false)

Categories should include: Essential Supplies, Home Safety, Documents,
Communication Plan, Medical Kit, Food & Water, Transportation.
"""

MULTILINGUAL_ALERT_PROMPT: str = """
You are an emergency alert system for monsoon conditions. Generate a
safety alert message in {language_name} language for:

- Location: {location}
- Weather Condition: {condition}
- Risk Level: {risk_level}

Respond as a JSON object with:
- "alert_title": Short, urgent title
- "alert_body": Detailed safety instructions (3-5 sentences)
- "action_items": Array of immediate actions to take
- "language": "{language}"
"""

WEATHER_ASSESSMENT_PROMPT: str = """
You are an expert meteorologist specializing in the Indian monsoon season.
Provide a realistic current monsoon weather assessment for the city of
{location} in India during the month of July 2026.

Consider the city's geographic location, typical monsoon patterns, historical
rainfall data, and current monsoon season behaviour. Be realistic and specific.

Respond ONLY as a valid JSON object with these exact keys:
- "city": The city name
- "temperature_c": Realistic temperature in Celsius (integer, typically 24-36 during monsoon)
- "humidity_percent": Realistic humidity percentage (integer, typically 65-98 during monsoon)
- "wind_speed_kmh": Wind speed in km/h (integer)
- "rainfall_mm": Expected rainfall in mm for today (integer)
- "condition": A short weather condition description (e.g., "Heavy Rain", "Thunderstorm", "Light Drizzle", "Overcast with Showers")
- "risk_level": One of "low", "moderate", "high", "severe" based on monsoon intensity
- "forecast_next_24h": A 1-2 sentence forecast for the next 24 hours specific to this location

Return ONLY the JSON object, no other text.
"""

TRAVEL_ADVISORY_PROMPT: str = """
You are a monsoon travel safety advisor for India. Generate a travel safety
assessment for someone traveling from {origin} to {destination} during the
active monsoon season (July 2026).

Consider:
- Current monsoon conditions at both locations
- Road and transportation risks (waterlogging, landslides, visibility)
- Route-specific hazards (ghats, flood-prone highways, river crossings)
- Historical monsoon travel incidents on this route

Respond ONLY as a valid JSON object with these exact keys:
- "origin_city": "{origin}"
- "destination_city": "{destination}"
- "risk_score": A float between 0.0 (safe) and 1.0 (extremely dangerous)
- "advisory_level": One of "SAFE TO TRAVEL", "MODERATE RISK", "TRAVEL WITH CAUTION", "DO NOT TRAVEL"
- "advisory_class": One of "low", "moderate", "high", "severe"
- "route_conditions": A 2-3 sentence description of current route conditions
- "precautions": Array of 3-6 specific safety precautions for this route
- "origin_weather_summary": Brief weather summary for {origin}
- "destination_weather_summary": Brief weather summary for {destination}

Return ONLY the JSON object, no other text.
"""
