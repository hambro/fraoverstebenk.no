from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, current_app

from fraoverstebenk import components
from fraoverstebenk.content import get_hat, load_hats

pages = Blueprint("pages", __name__)


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
