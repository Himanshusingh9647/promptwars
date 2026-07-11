"""
GenAI service tests with mock provider.

Validates JSON extraction, prompt generation, caching behaviour,
and provider factory. Tests use the MockGenAIProvider so no live
API calls are needed. The production app uses GoogleGenAIProvider.
"""

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.services.genai_service import (
    MockGenAIProvider,
    extract_json_from_response,
    generate_alert,
    generate_checklist,
    generate_preparedness_plan,
    get_genai_provider,
)


class TestExtractJsonFromResponse:
    """Test the JSON extraction utility for real Gemini responses."""

    def test_plain_json(self) -> None:
        """Direct JSON should parse correctly."""
        result = extract_json_from_response('{"key": "value"}')
        assert result == {"key": "value"}

    def test_json_in_code_block(self) -> None:
        """JSON wrapped in ```json code blocks should be extracted."""
        raw = '```json\n{"title": "Plan", "risk": "high"}\n```'
        result = extract_json_from_response(raw)
        assert result["title"] == "Plan"

    def test_json_in_plain_code_block(self) -> None:
        """JSON wrapped in ``` blocks (no language tag) should be extracted."""
        raw = '```\n{"title": "Test"}\n```'
        result = extract_json_from_response(raw)
        assert result["title"] == "Test"

    def test_json_with_surrounding_text(self) -> None:
        """JSON embedded in text should be extracted via brace matching."""
        raw = 'Here is your plan:\n{"title": "Plan", "items": []}\nHope this helps!'
        result = extract_json_from_response(raw)
        assert result["title"] == "Plan"

    def test_invalid_json_raises(self) -> None:
        """Completely invalid content should raise JSONDecodeError."""
        with pytest.raises(json.JSONDecodeError):
            extract_json_from_response("This is not JSON at all")

    def test_whitespace_handling(self) -> None:
        """JSON with surrounding whitespace should parse correctly."""
        raw = '   \n  {"key": "value"}  \n  '
        result = extract_json_from_response(raw)
        assert result["key"] == "value"

    def test_nested_json(self) -> None:
        """Nested JSON structures should parse correctly."""
        raw = '{"sections": [{"heading": "Test", "items": ["a", "b"]}]}'
        result = extract_json_from_response(raw)
        assert len(result["sections"]) == 1
        assert len(result["sections"][0]["items"]) == 2


class TestMockProvider:
    """Test the mock GenAI provider responses (used in tests only)."""

    def test_mock_plan_response(self, mock_genai: MockGenAIProvider) -> None:
        """Mock provider should return valid plan JSON."""
        response = mock_genai.generate("Generate a preparedness plan")
        data: dict[str, Any] = json.loads(response)
        assert "title" in data
        assert "risk_level" in data
        assert "sections" in data
        assert isinstance(data["sections"], list)

    def test_mock_checklist_response(self, mock_genai: MockGenAIProvider) -> None:
        """Mock provider should return valid checklist JSON."""
        response = mock_genai.generate("Generate a checklist")
        data: dict[str, Any] = json.loads(response)
        assert "title" in data
        assert "categories" in data
        for category in data["categories"]:
            assert "name" in category
            assert "items" in category

    def test_mock_alert_response(self, mock_genai: MockGenAIProvider) -> None:
        """Mock provider should return valid alert JSON."""
        response = mock_genai.generate("Generate an alert message")
        data: dict[str, Any] = json.loads(response)
        assert "alert_title" in data
        assert "alert_body" in data
        assert "action_items" in data

    def test_default_response_is_plan(self, mock_genai: MockGenAIProvider) -> None:
        """Non-specific prompts should default to plan response."""
        response = mock_genai.generate("Tell me about safety")
        data: dict[str, Any] = json.loads(response)
        assert "title" in data
        assert "sections" in data


class TestProviderFactory:
    """Test the GenAI provider factory function."""

    def test_mock_provider_creation(self) -> None:
        """Factory should create MockGenAIProvider for 'mock'."""
        provider = get_genai_provider("mock")
        assert isinstance(provider, MockGenAIProvider)

    def test_unknown_provider_raises(self) -> None:
        """Factory should raise ValueError for unknown provider."""
        with pytest.raises(ValueError, match="Unknown GenAI provider"):
            get_genai_provider("nonexistent")

    def test_default_provider_from_env(self) -> None:
        """Factory should read GENAI_PROVIDER from environment."""
        with patch.dict("os.environ", {"GENAI_PROVIDER": "mock"}):
            provider = get_genai_provider()
            assert isinstance(provider, MockGenAIProvider)


class TestGeneratePlan:
    """Test the high-level plan generation function."""

    @patch("app.services.genai_service.get_genai_provider")
    def test_generate_plan_returns_dict(self, mock_fn: MagicMock) -> None:
        """Plan generation should return a parsed dictionary."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = json.dumps({
            "title": "Test Plan", "risk_level": "high",
            "sections": [{"heading": "Test", "items": ["Item 1"]}],
            "emergency_contacts": ["112"],
        })
        mock_fn.return_value = mock_provider
        generate_preparedness_plan.cache_clear()

        result = generate_preparedness_plan(
            location="Mumbai", family_size=4,
            special_needs="None", language="en",
        )
        assert isinstance(result, dict)
        assert "title" in result

    def test_generate_plan_caching(self) -> None:
        """Repeated calls with same args should hit cache."""
        generate_preparedness_plan.cache_clear()

        with patch("app.services.genai_service.get_genai_provider") as mock_fn:
            mock_provider = MagicMock()
            mock_provider.generate.return_value = json.dumps({
                "title": "Cache Test", "risk_level": "low",
                "sections": [], "emergency_contacts": [],
            })
            mock_fn.return_value = mock_provider

            result1 = generate_preparedness_plan(
                location="CacheCity", family_size=3,
                special_needs="None", language="en",
            )
            result2 = generate_preparedness_plan(
                location="CacheCity", family_size=3,
                special_needs="None", language="en",
            )

            assert result1 == result2
            cache_info = generate_preparedness_plan.cache_info()
            assert cache_info.hits >= 1


class TestGenerateChecklist:
    """Test the checklist generation function."""

    @patch("app.services.genai_service.get_genai_provider")
    def test_generate_checklist_returns_dict(self, mock_fn: MagicMock) -> None:
        """Checklist generation should return parsed dict with categories."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = json.dumps({
            "title": "Test Checklist",
            "categories": [{"name": "Supplies", "items": [
                {"task": "Torch", "priority": "high", "completed": False},
            ]}],
        })
        mock_fn.return_value = mock_provider
        generate_checklist.cache_clear()

        result = generate_checklist(
            location="Chennai", family_size=5,
            special_needs="Elderly", language="en",
        )
        assert isinstance(result, dict)
        assert "categories" in result


class TestGenerateAlert:
    """Test the alert generation function."""

    @patch("app.services.genai_service.get_genai_provider")
    def test_generate_alert_returns_dict(self, mock_fn: MagicMock) -> None:
        """Alert generation should return parsed dict."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = json.dumps({
            "alert_title": "Test Alert",
            "alert_body": "Test body",
            "action_items": ["Action 1"],
            "language": "en",
        })
        mock_fn.return_value = mock_provider

        result = generate_alert(
            location="Mumbai", condition="Heavy Rain",
            risk_level="high", language="en",
        )
        assert isinstance(result, dict)
        assert "alert_title" in result
        assert "action_items" in result

    def test_generate_alert_not_cached(self) -> None:
        """Alert generation should NOT be cached (real-time data)."""
        assert not hasattr(generate_alert, "cache_info")
