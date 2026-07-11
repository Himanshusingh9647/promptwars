"""
Main blueprint routes — landing page and dashboard.

Serves the public-facing pages with server-side rendered templates.
"""

from flask import render_template

from app.blueprints.main import main_bp
from app.utils.constants import LANGUAGE_MAP, RISK_LEVELS


@main_bp.route("/")
def index() -> str:
    """
    Render the landing page.

    Passes language map and risk level data to the template for
    dynamic form population and visual indicators.

    Returns:
        Rendered HTML for the landing page.
    """
    return render_template(
        "index.html",
        languages=LANGUAGE_MAP,
        risk_levels=RISK_LEVELS,
    )


@main_bp.route("/dashboard")
def dashboard() -> str:
    """
    Render the interactive dashboard.

    Returns:
        Rendered HTML for the user dashboard.
    """
    return render_template(
        "dashboard.html",
        languages=LANGUAGE_MAP,
        risk_levels=RISK_LEVELS,
    )
