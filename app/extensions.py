"""
Flask extension initialization module.

Extensions are initialized here and bound to the app in the
application factory. This pattern prevents circular imports
and supports the application factory pattern.
"""

# Future extensions can be initialized here, e.g.:
# from flask_limiter import Limiter
# limiter = Limiter(key_func=get_remote_address)
#
# Then in create_app():
#   limiter.init_app(app)
