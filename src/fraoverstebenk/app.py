from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask

from fraoverstebenk.views import pages


def _mail_not_configured(subject: str, fields: dict[str, str]) -> None:
    raise RuntimeError("Mail sending is not configured")


def create_app(config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(Path.cwd() / "static"))
    app.config["CONTENT_DIR"] = Path("content")
    app.config["SEND_MAIL"] = _mail_not_configured
    if config:
        app.config.update(config)
    app.register_blueprint(pages)
    return app
