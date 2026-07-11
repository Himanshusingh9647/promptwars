"""
Preparedness blueprint — AI-powered plan and checklist generation.
"""

from flask import Blueprint

preparedness_bp = Blueprint("preparedness", __name__, url_prefix="/api/preparedness")

from app.blueprints.preparedness import routes  # noqa: E402, F401
