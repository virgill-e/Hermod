"""
PyPost — Factory Flask
create_app() initialise l'application Flask et enregistre les blueprints.
"""

from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__, static_folder="../ui", static_url_path="/")

    # ── Route racine : sert index.html ────────────────────────────────────────
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    # ── Blueprints (à décommenter au fur et à mesure) ─────────────────────────
    # from .routes_request import bp as request_bp
    # from .routes_collections import bp as collections_bp
    # from .routes_environments import bp as environments_bp
    # app.register_blueprint(request_bp)
    # app.register_blueprint(collections_bp)
    # app.register_blueprint(environments_bp)

    return app
