"""
Weather blueprint — real-time weather advisories and travel alerts.
"""

from flask import Blueprint

weather_bp = Blueprint("weather", __name__, url_prefix="/api/weather")

from app.blueprints.weather import routes  # noqa: E402, F401
