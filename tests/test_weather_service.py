"""
Weather service tests.

Tests use mocked Gemini responses to validate data processing,
field enrichment, and error handling without making live API calls.
The production app makes real Gemini calls.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.services.weather_service import get_current_weather, get_travel_advisory


# --------------------------------------------------------------------------- #
#  Mock Gemini response fixtures
# --------------------------------------------------------------------------- #

_MOCK_WEATHER_JSON: str = """{
    "city": "Mumbai",
    "temperature_c": 28,
    "humidity_percent": 89,
    "wind_speed_kmh": 35,
    "rainfall_mm": 120,
    "condition": "Heavy Rain",
    "risk_level": "high",
    "forecast_next_24h": "Continuous heavy rainfall expected with waterlogging in low-lying areas."
}"""

_MOCK_TRAVEL_JSON: str = """{
    "origin_city": "Pune",
    "destination_city": "Mumbai",
    "risk_score": 0.75,
    "advisory_level": "TRAVEL WITH CAUTION",
    "advisory_class": "high",
    "route_conditions": "Mumbai-Pune expressway has reduced visibility. Waterlogging reported near Lonavala.",
    "precautions": [
        "Avoid Khandala ghat section after dark",
        "Carry emergency supplies and extra fuel",
        "Check MSRDC traffic updates before departure"
    ],
    "origin_weather_summary": "Moderate rain in Pune",
    "destination_weather_summary": "Heavy rain in Mumbai"
}"""


class TestCurrentWeather:
    """Test AI-powered weather data retrieval."""

    def setup_method(self) -> None:
        """Clear weather cache before each test."""
        if hasattr(get_current_weather, "cache"):
            get_current_weather.cache.clear()  # type: ignore[attr-defined]

    @patch("app.services.weather_service.get_genai_provider")
    def test_returns_weather_data(self, mock_provider_fn: MagicMock) -> None:
        """Gemini response should be parsed into weather data."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = _MOCK_WEATHER_JSON
        mock_provider_fn.return_value = mock_provider

        data: dict[str, Any] = get_current_weather("Mumbai")
        assert data["city"] == "Mumbai"
        assert data["temperature_c"] == 28
        assert data["humidity_percent"] == 89
        assert data["rainfall_mm"] == 120
        assert data["risk_level"] == "high"

    @patch("app.services.weather_service.get_genai_provider")
    def test_enriches_with_risk_metadata(self, mock_provider_fn: MagicMock) -> None:
        """Weather data should include enriched risk label, color, description."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = _MOCK_WEATHER_JSON
        mock_provider_fn.return_value = mock_provider

        data = get_current_weather("Mumbai")
        assert "risk_label" in data
        assert "risk_color" in data
        assert "risk_description" in data
        assert data["risk_label"] == "High"

    @patch("app.services.weather_service.get_genai_provider")
    def test_normalizes_invalid_risk_level(self, mock_provider_fn: MagicMock) -> None:
        """Invalid risk_level from Gemini should be normalized to 'moderate'."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '{"city":"Test","risk_level":"extreme","temperature_c":30}'
        mock_provider_fn.return_value = mock_provider

        data = get_current_weather("TestCity")
        assert data["risk_level"] == "moderate"

    @patch("app.services.weather_service.get_genai_provider")
    def test_fallback_on_api_error(self, mock_provider_fn: MagicMock) -> None:
        """API failure should return a valid fallback structure."""
        mock_provider = MagicMock()
        mock_provider.generate.side_effect = RuntimeError("API down")
        mock_provider_fn.return_value = mock_provider

        data = get_current_weather("ErrorCity")
        assert data["city"] == "Errorcity"
        assert data["risk_level"] == "moderate"
        assert "forecast_next_24h" in data

    @patch("app.services.weather_service.get_genai_provider")
    def test_caching_returns_same_data(self, mock_provider_fn: MagicMock) -> None:
        """Repeated calls with same location should hit cache."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = _MOCK_WEATHER_JSON
        mock_provider_fn.return_value = mock_provider

        data1 = get_current_weather("CacheTest")
        data2 = get_current_weather("CacheTest")
        assert data1 == data2
        # Provider should only be called once due to caching
        assert mock_provider.generate.call_count == 1


class TestTravelAdvisory:
    """Test AI-powered travel advisory generation."""

    def setup_method(self) -> None:
        """Clear caches before each test."""
        if hasattr(get_travel_advisory, "cache"):
            get_travel_advisory.cache.clear()  # type: ignore[attr-defined]
        if hasattr(get_current_weather, "cache"):
            get_current_weather.cache.clear()  # type: ignore[attr-defined]

    @patch("app.services.weather_service.get_genai_provider")
    def test_advisory_structure(self, mock_provider_fn: MagicMock) -> None:
        """Travel advisory should contain all required fields."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = _MOCK_TRAVEL_JSON
        mock_provider_fn.return_value = mock_provider

        data = get_travel_advisory("Pune", "Mumbai")
        assert "combined_risk_score" in data
        assert "advisory_level" in data
        assert "advisory_class" in data
        assert "precautions" in data
        assert "origin" in data
        assert "destination" in data

    @patch("app.services.weather_service.get_genai_provider")
    def test_risk_score_is_float(self, mock_provider_fn: MagicMock) -> None:
        """Risk score should be a float between 0 and 1."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = _MOCK_TRAVEL_JSON
        mock_provider_fn.return_value = mock_provider

        data = get_travel_advisory("Pune", "Mumbai")
        assert isinstance(data["combined_risk_score"], float)
        assert 0.0 <= data["combined_risk_score"] <= 1.0

    @patch("app.services.weather_service.get_genai_provider")
    def test_advisory_level_valid(self, mock_provider_fn: MagicMock) -> None:
        """Advisory level should be one of the defined levels."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = _MOCK_TRAVEL_JSON
        mock_provider_fn.return_value = mock_provider

        valid_levels = {
            "SAFE TO TRAVEL", "MODERATE RISK",
            "TRAVEL WITH CAUTION", "DO NOT TRAVEL",
        }
        data = get_travel_advisory("Pune", "Mumbai")
        assert data["advisory_level"] in valid_levels

    @patch("app.services.weather_service.get_genai_provider")
    def test_precautions_non_empty(self, mock_provider_fn: MagicMock) -> None:
        """Precautions list should not be empty."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = _MOCK_TRAVEL_JSON
        mock_provider_fn.return_value = mock_provider

        data = get_travel_advisory("Pune", "Mumbai")
        assert len(data["precautions"]) > 0

    @patch("app.services.weather_service.get_genai_provider")
    def test_advisory_color_present(self, mock_provider_fn: MagicMock) -> None:
        """Advisory should include a color for UI rendering."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = _MOCK_TRAVEL_JSON
        mock_provider_fn.return_value = mock_provider

        data = get_travel_advisory("Pune", "Mumbai")
        assert "advisory_color" in data
        assert data["advisory_color"].startswith("#")
