from __future__ import annotations

import logging
from pathlib import Path

from flask import Blueprint, abort, current_app, redirect, request, url_for
from werkzeug.wrappers import Response

from fraoverstebenk import components
from fraoverstebenk.content import get_hat, get_post, load_hats, load_posts

pages = Blueprint("pages", __name__)

logger = logging.getLogger(__name__)


def _content_dir() -> Path:
    return Path(current_app.config["CONTENT_DIR"])


@pages.get("/")
def frontpage() -> str:
    hats = load_hats(_content_dir())
    hero_image = hats[0].photo or hats[0].image if hats else None
    return str(components.frontpage(hero_image))


@pages.get("/hatter/")
def hat_overview() -> str:
    return str(components.hat_overview(load_hats(_content_dir())))


@pages.get("/hatter/<slug>/")
def hat_detail(slug: str) -> Response:
    if get_hat(_content_dir(), slug) is None:
        abort(404)
    return redirect(url_for("pages.order_form", slug=slug))


def _read_form() -> dict[str, str] | None:
    if request.form.get("website"):
        return None
    return {
        "Navn": request.form.get("navn", "").strip(),
        "Telefon/e-post": request.form.get("kontakt", "").strip(),
        "Beskjed": request.form.get("melding", "").strip(),
    }


def _submit(subject: str, form: dict[str, str] | None) -> Response | tuple[str, int] | None:
    if form is None:
        return redirect(url_for("pages.thanks"))
    if not form["Navn"] or not form["Telefon/e-post"]:
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
        error = "Navn og telefon eller e-post må fylles ut."
        return str(components.order_form(hat, error=error)), 400
    return result


@pages.get("/takk")
def thanks() -> str:
    return str(components.thanks())


@pages.get("/kontakt")
def contact() -> str:
    return str(components.contact_page())


@pages.get("/fra-benken/")
def posts() -> str:
    return str(components.posts_page(load_posts(_content_dir())))


@pages.get("/fra-benken/<slug>/")
def post_detail(slug: str) -> str:
    post = get_post(_content_dir(), slug)
    if post is None:
        abort(404)
    return str(components.post_page(post))


@pages.get("/godt-a-vite/")
def posts_old() -> Response:
    return redirect(url_for("pages.posts"), code=301)
