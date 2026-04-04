"""
PyPost — Point d'entrée principal
Lance Flask dans un thread daemon puis ouvre la fenêtre pywebview.
"""

import os
import threading
import time
import logging

import webview
from api import create_app

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger("pypost")

# ── Config ─────────────────────────────────────────────────────────────────────
FLASK_PORT = 5000
FLASK_HOST = "127.0.0.1"   # localhost uniquement, ne jamais binder sur 0.0.0.0
BASE_URL = f"http://{FLASK_HOST}:{FLASK_PORT}"

WINDOW_TITLE = "PyPost"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800


def start_flask(app: object) -> None:
    """Démarre le serveur Flask (bloquant — à appeler dans un thread)."""
    log.info("Flask démarré sur %s", BASE_URL)
    # debug=False obligatoire : le reloader de Flask est incompatible avec les threads
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)


def wait_for_flask(timeout: float = 10.0) -> bool:
    """Attends que Flask soit prêt à accepter des connexions."""
    import socket

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((FLASK_HOST, FLASK_PORT), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def main() -> None:
    is_dev = os.environ.get("FLASK_ENV") == "development"
    if is_dev:
        log.info("Mode développement activé (outils de dev pywebview activés)")

    flask_app = create_app()

    # Lance Flask dans un thread daemon (s'arrête automatiquement avec le process)
    flask_thread = threading.Thread(target=start_flask, args=(flask_app,), daemon=True)
    flask_thread.start()

    # Attend que Flask soit prêt avant d'ouvrir la fenêtre
    if not wait_for_flask():
        log.error("Flask n'a pas démarré dans le délai imparti. Abandon.")
        return

    log.info("Ouverture de la fenêtre pywebview → %s", BASE_URL)
    window = webview.create_window(
        title=WINDOW_TITLE,
        url=BASE_URL,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        frameless=False,
        min_size=(900, 600),
    )

    # gui=None → pywebview choisit le meilleur backend natif (WKWebView sur macOS)
    webview.start(debug=is_dev)

    log.info("Fenêtre fermée. Fin du programme.")


if __name__ == "__main__":
    main()
