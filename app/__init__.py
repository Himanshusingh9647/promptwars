"""
Monsoon Preparedness & Citizen Assistance Platform.

Application factory module. Creates and configures the Flask
application using the factory pattern for testability and
environment-specific configuration.
"""

import logging
from typing import Optional

from flask import Flask, Response, jsonify

from app.config import get_config


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Application factory — creates and configures a Flask instance.

    Args:
        config_name: Environment name ('development', 'testing', 'production').
                     Defaults to the ``FLASK_ENV`` environment variable.

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    # ----- Configuration -------------------------------------------------- #
    config = get_config(config_name)
    app.config.from_object(config)

    # ----- Logging -------------------------------------------------------- #
    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ----- Register Blueprints -------------------------------------------- #
    _register_blueprints(app)

    # ----- Register Error Handlers ---------------------------------------- #
    _register_error_handlers(app)

    # ----- Health Check --------------------------------------------------- #
    @app.route("/health")
    def health_check() -> tuple[Response, int]:
        """Simple health check endpoint for load balancers."""
        return jsonify({"status": "healthy", "service": "monsoon-preparedness"}), 200

    app.logger.info("Monsoon Preparedness app created [config=%s]", config_name)
    return app


def _register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints.

    Each blueprint represents a logical microservice boundary:
    - main: Public-facing pages
    - preparedness: GenAI-powered plan/checklist APIs
    - weather: Weather data and travel advisory APIs
    """
    from app.blueprints.main import main_bp
    from app.blueprints.preparedness import preparedness_bp
    from app.blueprints.weather import weather_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(preparedness_bp)
    app.register_blueprint(weather_bp)


def _register_error_handlers(app: Flask) -> None:
    """Register custom error handlers for common HTTP errors."""

    @app.errorhandler(404)
    def not_found(error: Exception) -> tuple[Response, int]:
        return jsonify({"error": "Resource not found.", "status": 404}), 404

    @app.errorhandler(500)
    def internal_error(error: Exception) -> tuple[Response, int]:
        app.logger.error("Internal server error: %s", error)
        return jsonify({"error": "Internal server error.", "status": 500}), 500

    @app.errorhandler(405)
    def method_not_allowed(error: Exception) -> tuple[Response, int]:
        return jsonify({"error": "Method not allowed.", "status": 405}), 405
