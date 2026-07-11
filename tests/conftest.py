"""
Pytest configuration and shared fixtures.

Provides app, client, and mock service fixtures used across all
test modules. The test config uses 'testing' environment which sets
GENAI_PROVIDER=mock. Individual tests that need to mock Gemini at
the function level use unittest.mock.patch instead.
"""

import os
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.services.genai_service import MockGenAIProvider


@pytest.fixture(name="app")
def fixture_app() -> Generator[Flask, None, None]:
    """
    Create a Flask application configured for testing.

    Sets GENAI_PROVIDER to 'mock' via environment to ensure
    no live API calls are made during test runs.

    Yields:
        Flask app instance with testing config.
    """
    # Force mock provider for all tests
    os.environ["GENAI_PROVIDER"] = "mock"

    application = create_app("testing")

    yield application

    # Cleanup: clear any cached GenAI results between test sessions
    from app.services.genai_service import (
        generate_checklist,
        generate_preparedness_plan,
    )
    generate_preparedness_plan.cache_clear()
    generate_checklist.cache_clear()


@pytest.fixture(name="client")
def fixture_client(app: Flask) -> FlaskClient:
    """
    Create a Flask test client.

    Args:
        app: The test Flask application.

    Returns:
        Flask test client for making requests.
    """
    return app.test_client()


@pytest.fixture(name="mock_genai")
def fixture_mock_genai() -> MockGenAIProvider:
    """
    Provide a mock GenAI provider instance.

    Returns:
        MockGenAIProvider for testing without API calls.
    """
    return MockGenAIProvider()
