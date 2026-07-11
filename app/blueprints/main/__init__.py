"""
Main blueprint — landing page and dashboard routes.
"""

from flask import Blueprint

main_bp = Blueprint(
    "main",
    __name__,
    template_folder="../../templates",
    static_folder="../../static",
)

from app.blueprints.main import routes  # noqa: E402, F401
