"""
Application entry point.

Loads environment variables from ``.env`` and starts the Flask
development server. In production, use a WSGI server (gunicorn)
instead.
"""

from dotenv import load_dotenv

# Load environment variables BEFORE importing the app factory
load_dotenv()

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
