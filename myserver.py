import os
from threading import Thread

from flask import Flask

app = Flask(__name__)


@app.get("/")
def home():
    return "Discord AFK Bot is running.", 200


@app.get("/health")
def health():
    return {"status": "ok"}, 200


def run() -> None:
    # Render supplies PORT. Its documented default for web services is 10000.
    port = int(os.getenv("PORT", "10000"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def server_on() -> None:
    thread = Thread(target=run, name="render-health-server", daemon=True)
    thread.start()
