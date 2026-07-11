"""
Application configuration module.

Provides environment-specific configuration classes following the
12-factor app methodology. All secrets are loaded from environment
variables — never hardcoded.
"""

import os
from typing import Optional


class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "fallback-dev-key")
    GENAI_PROVIDER: str = os.environ.get("GENAI_PROVIDER", "mock")
    GENAI_API_KEY: Optional[str] = os.environ.get("GENAI_API_KEY")
    WEATHER_API_KEY: Optional[str] = os.environ.get("WEATHER_API_KEY")
    WEATHER_CACHE_TTL_SECONDS: int = int(
        os.environ.get("WEATHER_CACHE_TTL_SECONDS", "300")
    )
    DEFAULT_LANGUAGE: str = os.environ.get("DEFAULT_LANGUAGE", "en")
    SUPPORTED_LANGUAGES: list[str] = os.environ.get(
        "SUPPORTED_LANGUAGES", "en,hi,bn,ta,te,mr,kn"
    ).split(",")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    DEBUG: bool = True
    TESTING: bool = False


class TestingConfig(BaseConfig):
    """Testing environment configuration with mock defaults."""

    DEBUG: bool = False
    TESTING: bool = True
    SECRET_KEY: str = "test-secret-key"
    GENAI_PROVIDER: str = "mock"
    WEATHER_CACHE_TTL_SECONDS: int = 0


class ProductionConfig(BaseConfig):
    """Production environment configuration with strict security."""

    DEBUG: bool = False
    TESTING: bool = False


CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(config_name: Optional[str] = None) -> BaseConfig:
    """
    Retrieve the configuration class for the specified environment.

    Args:
        config_name: Environment name ('development', 'testing', 'production').
                     Defaults to FLASK_ENV environment variable.

    Returns:
        An instance of the appropriate configuration class.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    config_class = CONFIG_MAP.get(config_name, DevelopmentConfig)
    return config_class()
