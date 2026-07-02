from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask

from fraoverstebenk import mail
from fraoverstebenk.views import pages


def _send_mail_from_env(subject: str, fields: dict[str, str]) -> None:
    mail.send_form_email(mail.settings_from_env(), subject, fields)


def create_app(config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(Path.cwd() / "static"))
    app.config["CONTENT_DIR"] = Path("content")
    app.config["SEND_MAIL"] = _send_mail_from_env
    if config:
        app.config.update(config)
    app.register_blueprint(pages)
    return app
