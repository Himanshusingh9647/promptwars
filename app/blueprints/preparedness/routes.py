"""
Preparedness blueprint routes — GenAI-powered plan and checklist APIs.

All user input is validated and sanitized before reaching the GenAI
service to prevent prompt injection and ensure data integrity.
"""

from typing import Any

from flask import Response, jsonify, request

from app.blueprints.preparedness import preparedness_bp
from app.services.genai_service import (
    generate_alert,
    generate_checklist,
    generate_preparedness_plan,
)
from app.utils.validators import (
    ValidationError,
    validate_family_size,
    validate_language,
    validate_location,
    validate_special_needs,
)


@preparedness_bp.route("/plan", methods=["POST"])
def create_plan() -> tuple[Response, int]:
    """
    Generate a personalized monsoon preparedness plan.

    Expects JSON body with:
        - location (str): City or region name.
        - family_size (int): Number of family members.
        - special_needs (str, optional): Special requirements.
        - language (str, optional): ISO language code (default: 'en').

    Returns:
        JSON response with the generated plan or error details.
    """
    data: dict[str, Any] = request.get_json(silent=True) or {}

    try:
        location: str = validate_location(data.get("location", ""))
        family_size: int = validate_family_size(data.get("family_size", 0))
        special_needs: str = validate_special_needs(data.get("special_needs"))
        language: str = validate_language(data.get("language", "en"))
    except ValidationError as exc:
        return jsonify({"error": exc.message, "field": exc.field}), 400

    try:
        plan: dict[str, Any] = generate_preparedness_plan(
            location=location,
            family_size=family_size,
            special_needs=special_needs,
            language=language,
        )
        return jsonify({"status": "success", "data": plan}), 200
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503


@preparedness_bp.route("/checklist", methods=["POST"])
def create_checklist() -> tuple[Response, int]:
    """
    Generate a monsoon emergency checklist.

    Expects JSON body with:
        - location (str): City or region name.
        - family_size (int): Number of family members.
        - special_needs (str, optional): Special requirements.
        - language (str, optional): ISO language code (default: 'en').

    Returns:
        JSON response with the categorised checklist or error details.
    """
    data: dict[str, Any] = request.get_json(silent=True) or {}

    try:
        location: str = validate_location(data.get("location", ""))
        family_size: int = validate_family_size(data.get("family_size", 0))
        special_needs: str = validate_special_needs(data.get("special_needs"))
        language: str = validate_language(data.get("language", "en"))
    except ValidationError as exc:
        return jsonify({"error": exc.message, "field": exc.field}), 400

    try:
        checklist: dict[str, Any] = generate_checklist(
            location=location,
            family_size=family_size,
            special_needs=special_needs,
            language=language,
        )
        return jsonify({"status": "success", "data": checklist}), 200
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503


@preparedness_bp.route("/alert", methods=["POST"])
def create_alert() -> tuple[Response, int]:
    """
    Generate a multilingual safety alert.

    Expects JSON body with:
        - location (str): Affected location.
        - condition (str): Weather condition description.
        - risk_level (str): One of 'low', 'moderate', 'high', 'severe'.
        - language (str, optional): ISO language code (default: 'en').

    Returns:
        JSON response with the alert content.
    """
    data: dict[str, Any] = request.get_json(silent=True) or {}

    try:
        location: str = validate_location(data.get("location", ""))
        language: str = validate_language(data.get("language", "en"))
    except ValidationError as exc:
        return jsonify({"error": exc.message, "field": exc.field}), 400

    # Validate condition and risk_level with basic sanitization
    condition: str = data.get("condition", "Heavy Rain").strip()[:200]
    risk_level: str = data.get("risk_level", "moderate")
    if risk_level not in ("low", "moderate", "high", "severe"):
        return jsonify({"error": "Invalid risk level.", "field": "risk_level"}), 400

    try:
        alert: dict[str, Any] = generate_alert(
            location=location,
            condition=condition,
            risk_level=risk_level,
            language=language,
        )
        return jsonify({"status": "success", "data": alert}), 200
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
