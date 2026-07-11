"""
Application factory and configuration tests.

Validates that the app factory correctly creates Flask instances
with proper configuration, blueprint registration, and error handling.
"""

from flask import Flask

from app.config import DevelopmentConfig, ProductionConfig, TestingConfig, get_config


class TestConfig:
    """Test configuration class loading."""

    def test_development_config(self) -> None:
        """Development config should enable debug mode."""
        config = get_config("development")
        assert isinstance(config, DevelopmentConfig)
        assert config.DEBUG is True
        assert config.TESTING is False

    def test_testing_config(self) -> None:
        """Testing config should use mock provider and disable debug."""
        config = get_config("testing")
        assert isinstance(config, TestingConfig)
        assert config.DEBUG is False
        assert config.TESTING is True
        assert config.GENAI_PROVIDER == "mock"
        assert config.SECRET_KEY == "test-secret-key"

    def test_production_config(self) -> None:
        """Production config should disable both debug and testing."""
        config = get_config("production")
        assert isinstance(config, ProductionConfig)
        assert config.DEBUG is False
        assert config.TESTING is False

    def test_default_config_is_development(self) -> None:
        """Default config should fall back to development."""
        config = get_config("nonexistent")
        assert isinstance(config, DevelopmentConfig)

    def test_supported_languages_is_list(self) -> None:
        """Supported languages should be parsed as a list."""
        config = get_config("testing")
        assert isinstance(config.SUPPORTED_LANGUAGES, list)
        assert "en" in config.SUPPORTED_LANGUAGES


class TestAppFactory:
    """Test the application factory pattern."""

    def test_create_app_returns_flask_instance(self, app: Flask) -> None:
        """Factory should return a valid Flask application."""
        assert isinstance(app, Flask)

    def test_testing_flag_set(self, app: Flask) -> None:
        """Testing flag should be set in test configuration."""
        assert app.config["TESTING"] is True

    def test_blueprints_registered(self, app: Flask) -> None:
        """All expected blueprints should be registered."""
        blueprint_names = list(app.blueprints.keys())
        assert "main" in blueprint_names
        assert "preparedness" in blueprint_names
        assert "weather" in blueprint_names

    def test_health_endpoint(self, client) -> None:
        """Health check should return 200 with status 'healthy'."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "monsoon-preparedness"


class TestErrorHandlers:
    """Test custom error handlers."""

    def test_404_handler(self, client) -> None:
        """Non-existent route should return JSON 404."""
        response = client.get("/this-does-not-exist")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "Resource not found."

    def test_405_handler(self, client) -> None:
        """Wrong HTTP method should return JSON 405."""
        response = client.delete("/health")
        assert response.status_code == 405
        data = response.get_json()
        assert data["error"] == "Method not allowed."
