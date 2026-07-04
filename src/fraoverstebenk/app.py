from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask, Response, request

from fraoverstebenk import components, mail
from fraoverstebenk.views import pages

CSP = (
    "default-src 'none'; "
    "img-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "font-src 'self'; "
    "form-action 'self'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'"
)

LONG_CACHE_SUFFIXES = (".woff2", ".png", ".svg", ".jpg", ".jpeg", ".webp", ".ico")


def _send_mail_from_env(subject: str, fields: dict[str, str]) -> None:
    mail.send_form_email(mail.settings_from_env(), subject, fields)


def _not_found(_: Exception) -> tuple[str, int]:
    return str(components.not_found()), 404


def _set_headers(response: Response) -> Response:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
    response.headers.setdefault("Content-Security-Policy", CSP)
    if request.path.startswith("/static/"):
        if request.path.endswith(LONG_CACHE_SUFFIXES):
            response.headers["Cache-Control"] = "public, max-age=2592000"
        else:
            response.headers["Cache-Control"] = "public, max-age=3600"
    return response


def create_app(config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(Path.cwd() / "static"))
    app.config["CONTENT_DIR"] = Path("content")
    app.config["SEND_MAIL"] = _send_mail_from_env
    if config:
        app.config.update(config)
    app.register_blueprint(pages)
    app.register_error_handler(404, _not_found)
    app.after_request(_set_headers)
    return app
