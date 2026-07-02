from __future__ import annotations

import logging
from pathlib import Path

from flask import Blueprint, abort, current_app, redirect, request, url_for
from werkzeug.wrappers import Response

from fraoverstebenk import components
from fraoverstebenk.content import get_hat, load_hats, load_posts

pages = Blueprint("pages", __name__)

logger = logging.getLogger(__name__)


def _content_dir() -> Path:
    return Path(current_app.config["CONTENT_DIR"])


@pages.get("/")
def frontpage() -> str:
    return str(components.frontpage())


@pages.get("/hatter/")
def hat_overview() -> str:
    return str(components.hat_overview(load_hats(_content_dir())))


@pages.get("/hatter/<slug>/")
def hat_detail(slug: str) -> str:
    hat = get_hat(_content_dir(), slug)
    if hat is None:
        abort(404)
    return str(components.hat_detail(hat))


def _read_form() -> dict[str, str] | None:
    if request.form.get("website"):
        return None
    return {
        "Navn": request.form.get("navn", "").strip(),
        "Telefon": request.form.get("telefon", "").strip(),
        "Melding": request.form.get("melding", "").strip(),
    }


def _submit(subject: str, form: dict[str, str] | None) -> Response | tuple[str, int] | None:
    if form is None:
        return redirect(url_for("pages.thanks"))
    if not form["Navn"] or not form["Telefon"]:
        return None
    try:
        current_app.config["SEND_MAIL"](subject, form)
    except Exception:
        logger.exception("Kunne ikke sende e-post. Innhold: %r", form)
        return str(components.mail_error()), 500
    return redirect(url_for("pages.thanks"))


@pages.get("/hatter/<slug>/bestill")
def order_form(slug: str) -> str:
    hat = get_hat(_content_dir(), slug)
    if hat is None:
        abort(404)
    return str(components.order_form(hat))


@pages.post("/hatter/<slug>/bestill")
def order_submit(slug: str) -> Response | tuple[str, int]:
    hat = get_hat(_content_dir(), slug)
    if hat is None:
        abort(404)
    result = _submit(f"Bestilling: {hat.title}", _read_form())
    if result is None:
        return str(components.order_form(hat, error="Navn og telefon må fylles ut.")), 400
    return result


@pages.get("/takk")
def thanks() -> str:
    return str(components.thanks())


@pages.get("/kontakt")
def contact() -> str:
    return str(components.contact_page())


@pages.post("/kontakt")
def contact_submit() -> Response | tuple[str, int]:
    result = _submit("Kontaktskjema", _read_form())
    if result is None:
        return str(components.contact_page(error="Navn og telefon må fylles ut.")), 400
    return result


@pages.get("/godt-a-vite/")
def posts() -> str:
    return str(components.posts_page(load_posts(_content_dir())))
