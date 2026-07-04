from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from fraoverstebenk.app import create_app

HAT = """---
title: Solnedgang
meta: no. 014 · gradient, prikket · 1 190 kr
accent: "#FF4E2E"
image: /static/images/hatter/solnedgang.svg
price: 1190
sort: 1
---
Gul topp som glir over i **dyp rød**.
"""

POST = """---
title: Stell av hatten
date: 2026-06-01
tag: tips og triks
color: "#43B54A"
teaser: Slik holder hatten seg fin i mange år.
---
Børst hatten forsiktig.
"""


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    hat_dir = tmp_path / "hatter"
    hat_dir.mkdir()
    (hat_dir / "solnedgang.md").write_text(HAT, encoding="utf-8")
    post_dir = tmp_path / "fra-benken"
    post_dir.mkdir()
    (post_dir / "stell-av-hatten.md").write_text(POST, encoding="utf-8")
    return tmp_path


@pytest.fixture
def sent_mail() -> list[tuple[str, dict[str, str]]]:
    return []


@pytest.fixture
def app(content_dir: Path, sent_mail: list[tuple[str, dict[str, str]]]) -> Flask:
    def record_mail(subject: str, fields: dict[str, str]) -> None:
        sent_mail.append((subject, fields))

    return create_app({"CONTENT_DIR": content_dir, "SEND_MAIL": record_mail, "TESTING": True})


@pytest.fixture
def client(app: Flask) -> Iterator[FlaskClient]:
    with app.test_client() as test_client:
        yield test_client
