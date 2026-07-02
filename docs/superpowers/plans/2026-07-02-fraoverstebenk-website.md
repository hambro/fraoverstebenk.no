# fraøverstebenk.no Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Flask + htpy website for fraøverstebenk.no with markdown-backed hats and posts, order/contact forms that email the owner, and Docker/Traefik deployment.

**Architecture:** Flask app factory with one blueprint; all HTML built with htpy components (no templates); content parsed from markdown files with YAML frontmatter on every request; email over plain SMTP injected via `app.config["SEND_MAIL"]` so tests can record instead of send.

**Tech Stack:** Python 3.13, Flask, htpy, python-frontmatter, markdown, gunicorn, uv, mise, ruff, mypy (strict), pytest, Docker + Traefik.

## Global Constraints

- Python `>=3.13`; deps managed by uv; tool versions pinned in `mise.toml`.
- mypy strict mode must pass; ruff check + format must pass. All checked before every commit.
- Code comments only on their own line, never trailing code (user rule).
- All user-facing copy is Norwegian (bokmål).
- The site name renders as "fra øverste benk"; the deployed hosts are the punycode `xn--fraverstebenk-dnb.no` and `www.xn--fraverstebenk-dnb.no`.
- Honeypot form field is named `website`; a filled honeypot pretends success and sends nothing.
- Content is read per request from `content/` — no caching layer.
- Verification command for every task: `uv run pytest && uv run mypy . && uv run ruff check . && uv run ruff format --check .`

---

### Task 1: Project scaffold + app factory

**Files:**
- Create: `mise.toml`, `pyproject.toml`, `.gitignore`, `src/fraoverstebenk/__init__.py`, `src/fraoverstebenk/app.py`, `tests/__init__.py`, `tests/test_app.py`

**Interfaces:**
- Produces: `create_app(config: dict[str, Any] | None = None) -> Flask` in `fraoverstebenk.app`. Config keys used later: `CONTENT_DIR` (Path, default `Path("content")`), `SEND_MAIL` (callable `(subject: str, fields: dict[str, str]) -> None`, default raises until Task 5 wires the real sender).

- [ ] **Step 1: Write config files**

`mise.toml`:

```toml
[tools]
python = "3.13"
uv = "latest"

[tasks.dev]
run = "uv run flask --app fraoverstebenk.app:create_app --debug run"

[tasks.test]
run = "uv run pytest"

[tasks.lint]
run = "uv run ruff check . && uv run ruff format --check ."

[tasks.typecheck]
run = "uv run mypy ."

[tasks.check]
depends = ["test", "lint", "typecheck"]
```

`pyproject.toml`:

```toml
[project]
name = "fraoverstebenk"
version = "0.1.0"
description = "Nettsiden til fra øverste benk"
requires-python = ">=3.13"
dependencies = [
    "flask>=3.1",
    "htpy>=25.6",
    "markdown>=3.8",
    "python-frontmatter>=1.1",
    "gunicorn>=23.0",
]

[dependency-groups]
dev = [
    "pytest>=8.4",
    "mypy>=1.16",
    "ruff>=0.12",
    "types-markdown",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/fraoverstebenk"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
strict = true
files = ["src", "tests"]
mypy_path = "src"

[[tool.mypy.overrides]]
module = "frontmatter.*"
ignore_missing_imports = true
```

`.gitignore`:

```
.venv/
__pycache__/
*.pyc
.env
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

- [ ] **Step 2: Write the failing test**

`tests/__init__.py`: empty file.

`tests/test_app.py`:

```python
from fraoverstebenk.app import create_app


def test_create_app_returns_flask_app() -> None:
    app = create_app()
    assert app.name == "fraoverstebenk.app"


def test_config_overrides_are_applied() -> None:
    app = create_app({"CONTENT_DIR": "somewhere"})
    assert app.config["CONTENT_DIR"] == "somewhere"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv sync && uv run pytest -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'fraoverstebenk.app'` (or ImportError).

- [ ] **Step 4: Write minimal implementation**

`src/fraoverstebenk/__init__.py`: empty file.

`src/fraoverstebenk/app.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask


def _mail_not_configured(subject: str, fields: dict[str, str]) -> None:
    raise RuntimeError("Mail sending is not configured")


def create_app(config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(Path.cwd() / "static"))
    app.config["CONTENT_DIR"] = Path("content")
    app.config["SEND_MAIL"] = _mail_not_configured
    if config:
        app.config.update(config)
    return app
```

- [ ] **Step 5: Verify everything passes**

Run: `uv run pytest && uv run mypy . && uv run ruff check . && uv run ruff format --check .`
Expected: 2 passed; mypy: no issues; ruff: clean. If `ruff format --check` complains, run `uv run ruff format .`.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: project scaffold with Flask app factory"
```

---

### Task 2: Hat content loading

**Files:**
- Create: `src/fraoverstebenk/content.py`, `tests/test_content.py`

**Interfaces:**
- Produces in `fraoverstebenk.content`:
  - `@dataclass(frozen=True) Hat: slug: str, title: str, subtitle: str, image: str, sort: int, description: Markup`
  - `load_hats(content_dir: Path) -> list[Hat]` — sorted by `(sort, slug)`, skips malformed files with a warning log
  - `get_hat(content_dir: Path, slug: str) -> Hat | None`

- [ ] **Step 1: Write the failing tests**

`tests/test_content.py`:

```python
from pathlib import Path

import pytest

from fraoverstebenk.content import get_hat, load_hats


def write_hat(content_dir: Path, slug: str, body: str) -> None:
    hat_dir = content_dir / "hatter"
    hat_dir.mkdir(parents=True, exist_ok=True)
    (hat_dir / f"{slug}.md").write_text(body, encoding="utf-8")


VINTERLUE = """---
title: Vinterlue
subtitle: Varm og god
image: /static/images/hatter/vinterlue.svg
sort: 2
---
En **varm** lue for kalde dager.
"""

SOLHATT = """---
title: Solhatt
subtitle: Bred brem
image: /static/images/hatter/solhatt.svg
sort: 1
---
Skjermer mot sol.
"""


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    write_hat(tmp_path, "vinterlue", VINTERLUE)
    write_hat(tmp_path, "solhatt", SOLHATT)
    return tmp_path


def test_load_hats_parses_frontmatter_and_body(content_dir: Path) -> None:
    hats = load_hats(content_dir)
    assert [hat.slug for hat in hats] == ["solhatt", "vinterlue"]
    vinterlue = hats[1]
    assert vinterlue.title == "Vinterlue"
    assert vinterlue.subtitle == "Varm og god"
    assert vinterlue.image == "/static/images/hatter/vinterlue.svg"
    assert "<strong>varm</strong>" in str(vinterlue.description)


def test_load_hats_skips_malformed_files(content_dir: Path) -> None:
    write_hat(content_dir, "broken", "---\ntitle: Bare tittel\n---\nMangler resten.\n")
    hats = load_hats(content_dir)
    assert [hat.slug for hat in hats] == ["solhatt", "vinterlue"]


def test_load_hats_with_missing_directory(tmp_path: Path) -> None:
    assert load_hats(tmp_path) == []


def test_get_hat_by_slug(content_dir: Path) -> None:
    hat = get_hat(content_dir, "solhatt")
    assert hat is not None
    assert hat.title == "Solhatt"


def test_get_hat_unknown_slug(content_dir: Path) -> None:
    assert get_hat(content_dir, "finnes-ikke") is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_content.py -v`
Expected: FAIL with ImportError (no `content` module).

- [ ] **Step 3: Write the implementation**

`src/fraoverstebenk/content.py`:

```python
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import frontmatter
import markdown
from markupsafe import Markup

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Hat:
    slug: str
    title: str
    subtitle: str
    image: str
    sort: int
    description: Markup


def _render_markdown(text: str) -> Markup:
    return Markup(markdown.markdown(text))


def _load_hat(path: Path) -> Hat | None:
    try:
        parsed = frontmatter.load(path)
        return Hat(
            slug=path.stem,
            title=str(parsed["title"]),
            subtitle=str(parsed["subtitle"]),
            image=str(parsed["image"]),
            sort=int(parsed.get("sort", 0)),
            description=_render_markdown(parsed.content),
        )
    except (KeyError, ValueError) as error:
        logger.warning("Hopper over %s: %s", path, error)
        return None


def load_hats(content_dir: Path) -> list[Hat]:
    hats = [
        hat
        for path in sorted((content_dir / "hatter").glob("*.md"))
        if (hat := _load_hat(path)) is not None
    ]
    return sorted(hats, key=lambda hat: (hat.sort, hat.slug))


def get_hat(content_dir: Path, slug: str) -> Hat | None:
    for hat in load_hats(content_dir):
        if hat.slug == slug:
            return hat
    return None
```

Note: `(content_dir / "hatter").glob("*.md")` on a missing directory returns an empty iterator on Python 3.13, so no existence check is needed.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_content.py -v && uv run mypy . && uv run ruff check . && uv run ruff format --check .`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: load hats from markdown with frontmatter"
```

---

### Task 3: Post content loading

**Files:**
- Modify: `src/fraoverstebenk/content.py`
- Test: `tests/test_content.py`

**Interfaces:**
- Produces in `fraoverstebenk.content`:
  - `@dataclass(frozen=True) Post: slug: str, title: str, published: datetime.date, body: Markup`
  - `load_posts(content_dir: Path) -> list[Post]` — newest first, skips malformed files

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_content.py`:

```python
from fraoverstebenk.content import load_posts


def write_post(content_dir: Path, filename: str, body: str) -> None:
    post_dir = content_dir / "godt-a-vite"
    post_dir.mkdir(parents=True, exist_ok=True)
    (post_dir / filename).write_text(body, encoding="utf-8")


STELL = """---
title: Stell av hatten
date: 2026-06-01
---
Børst hatten *forsiktig*.
"""

STORRELSE = """---
title: Finn riktig størrelse
date: 2026-06-15
---
Mål rundt hodet.
"""


def test_load_posts_newest_first(tmp_path: Path) -> None:
    write_post(tmp_path, "2026-06-01-stell.md", STELL)
    write_post(tmp_path, "2026-06-15-storrelse.md", STORRELSE)
    posts = load_posts(tmp_path)
    assert [post.title for post in posts] == ["Finn riktig størrelse", "Stell av hatten"]
    assert "<em>forsiktig</em>" in str(posts[1].body)


def test_load_posts_skips_malformed(tmp_path: Path) -> None:
    write_post(tmp_path, "2026-06-01-stell.md", STELL)
    write_post(tmp_path, "ugyldig.md", "---\ntitle: Uten dato\n---\nHei.\n")
    posts = load_posts(tmp_path)
    assert [post.title for post in posts] == ["Stell av hatten"]


def test_load_posts_with_missing_directory(tmp_path: Path) -> None:
    assert load_posts(tmp_path) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_content.py -v`
Expected: new tests FAIL with ImportError (`load_posts`).

- [ ] **Step 3: Write the implementation**

Append to `src/fraoverstebenk/content.py` (add `import datetime` at the top with the other imports):

```python
@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    published: datetime.date
    body: Markup


def _load_post(path: Path) -> Post | None:
    try:
        parsed = frontmatter.load(path)
        published = parsed["date"]
        if not isinstance(published, datetime.date):
            raise ValueError(f"date is not a date: {published!r}")
        return Post(
            slug=path.stem,
            title=str(parsed["title"]),
            published=published,
            body=_render_markdown(parsed.content),
        )
    except (KeyError, ValueError) as error:
        logger.warning("Hopper over %s: %s", path, error)
        return None


def load_posts(content_dir: Path) -> list[Post]:
    posts = [
        post
        for path in sorted((content_dir / "godt-a-vite").glob("*.md"))
        if (post := _load_post(path)) is not None
    ]
    return sorted(posts, key=lambda post: post.published, reverse=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest && uv run mypy . && uv run ruff check . && uv run ruff format --check .`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: load godt-å-vite posts from markdown"
```

---

### Task 4: Layout, frontpage, and hat pages

**Files:**
- Create: `src/fraoverstebenk/components.py`, `src/fraoverstebenk/views.py`, `tests/conftest.py`, `tests/test_pages.py`
- Modify: `src/fraoverstebenk/app.py`

**Interfaces:**
- Consumes: `load_hats`, `get_hat`, `Hat` from Task 2.
- Produces:
  - `fraoverstebenk.views.pages` — a `Blueprint` registered by `create_app`
  - `fraoverstebenk.components.layout(page_title: str, content: Node) -> Element`
  - Component functions `frontpage()`, `hat_overview(hats)`, `hat_detail(hat)` returning htpy `Element`s
  - Test fixtures in `tests/conftest.py`: `app`, `client`, `content_dir` (session-shaped as below) used by all later page tests

- [ ] **Step 1: Write test fixtures and failing tests**

`tests/conftest.py`:

```python
from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from fraoverstebenk.app import create_app

HAT = """---
title: Solhatt
subtitle: Bred brem mot sol
image: /static/images/hatter/solhatt.svg
sort: 1
---
En hatt med **bred brem**.
"""

POST = """---
title: Stell av hatten
date: 2026-06-01
---
Børst hatten forsiktig.
"""


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    hat_dir = tmp_path / "hatter"
    hat_dir.mkdir()
    (hat_dir / "solhatt.md").write_text(HAT, encoding="utf-8")
    post_dir = tmp_path / "godt-a-vite"
    post_dir.mkdir()
    (post_dir / "2026-06-01-stell.md").write_text(POST, encoding="utf-8")
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
```

`tests/test_pages.py`:

```python
from flask.testing import FlaskClient


def test_frontpage(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "fra øverste benk" in response.get_data(as_text=True)


def test_hat_overview_shows_hats(client: FlaskClient) -> None:
    response = client.get("/hatter/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Kaldt hode kolleksjon" in body
    assert "Solhatt" in body
    assert "Bred brem mot sol" in body
    assert "/static/images/hatter/solhatt.svg" in body
    assert "/hatter/solhatt/" in body


def test_hat_detail(client: FlaskClient) -> None:
    response = client.get("/hatter/solhatt/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Solhatt" in body
    assert "<strong>bred brem</strong>" in body
    assert "/hatter/solhatt/bestill" in body


def test_hat_detail_unknown_slug_404(client: FlaskClient) -> None:
    assert client.get("/hatter/finnes-ikke/").status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_pages.py -v`
Expected: FAIL — `/` returns 404 (no routes registered yet).

- [ ] **Step 3: Write components**

`src/fraoverstebenk/components.py`:

```python
from __future__ import annotations

from htpy import (
    Element,
    Node,
    a,
    article,
    body,
    div,
    footer,
    h1,
    h2,
    h3,
    head,
    header,
    html,
    img,
    li,
    link,
    main,
    meta,
    nav,
    p,
    section,
    title,
    ul,
)

from fraoverstebenk.content import Hat

SITE_NAME = "fra øverste benk"


def layout(page_title: str, content: Node) -> Element:
    return html(lang="no")[
        head[
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            title[f"{page_title} – {SITE_NAME}"],
            link(rel="stylesheet", href="/static/style.css"),
        ],
        body[
            header[
                a(".site-name", href="/")[SITE_NAME],
                nav[
                    a(href="/hatter/")["Hatter"],
                    a(href="/godt-a-vite/")["Godt å vite"],
                    a(href="/kontakt")["Kontakt"],
                ],
            ],
            main[content],
            footer[p[SITE_NAME]],
        ],
    ]


def frontpage() -> Element:
    return layout(
        "Hjem",
        section[
            h1[SITE_NAME],
            p["Håndplukkede hatter fra øverste benk."],
            p[a(href="/hatter/")["Se kolleksjonen"]],
        ],
    )


def hat_card(hat: Hat) -> Element:
    return li[
        a(href=f"/hatter/{hat.slug}/")[
            img(src=hat.image, alt=hat.title),
            h3[hat.title],
            p[hat.subtitle],
        ]
    ]


def hat_overview(hats: list[Hat]) -> Element:
    return layout(
        "Hatter",
        section[
            h1["Kaldt hode kolleksjon"],
            ul(".hats")[[hat_card(hat) for hat in hats]],
        ],
    )


def hat_detail(hat: Hat) -> Element:
    return layout(
        hat.title,
        article[
            h1[hat.title],
            h2[hat.subtitle],
            img(src=hat.image, alt=hat.title),
            div[hat.description],
            p[a(".button", href=f"/hatter/{hat.slug}/bestill")["Kjøp"]],
        ],
    )
```

- [ ] **Step 4: Write views and register the blueprint**

`src/fraoverstebenk/views.py`:

```python
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
```

In `src/fraoverstebenk/app.py`, import and register the blueprint inside `create_app` right before `return app`:

```python
from fraoverstebenk.views import pages
```

```python
    app.register_blueprint(pages)
```

(The import goes at module top; keep the existing imports.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest && uv run mypy . && uv run ruff check . && uv run ruff format --check .`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: layout, frontpage and hat pages"
```

---

### Task 5: SMTP mail sending

**Files:**
- Create: `src/fraoverstebenk/mail.py`, `tests/test_mail.py`
- Modify: `src/fraoverstebenk/app.py`

**Interfaces:**
- Produces in `fraoverstebenk.mail`:
  - `@dataclass(frozen=True) MailSettings: host: str, port: int, username: str, password: str, from_addr: str, to_addr: str`
  - `settings_from_env(env: Mapping[str, str] | None = None) -> MailSettings` — reads `SMTP_HOST`, `SMTP_PORT` (default "587"), `SMTP_USERNAME`, `SMTP_PASSWORD`, `MAIL_FROM`, `MAIL_TO`; `env=None` means `os.environ`
  - `send_form_email(settings: MailSettings, subject: str, fields: dict[str, str]) -> None` — STARTTLS, login, send
- `app.py` gains `_send_mail_from_env(subject, fields)` as the default `SEND_MAIL`, replacing `_mail_not_configured`.

- [ ] **Step 1: Write the failing tests**

`tests/test_mail.py`:

```python
from unittest import mock

import pytest

from fraoverstebenk.mail import MailSettings, send_form_email, settings_from_env

ENV = {
    "SMTP_HOST": "smtp.example.com",
    "SMTP_USERNAME": "bruker",
    "SMTP_PASSWORD": "hemmelig",
    "MAIL_FROM": "nettside@example.com",
    "MAIL_TO": "carl@example.com",
}


def test_settings_from_env_with_default_port() -> None:
    settings = settings_from_env(ENV)
    assert settings.host == "smtp.example.com"
    assert settings.port == 587
    assert settings.to_addr == "carl@example.com"


def test_settings_from_env_missing_variable_raises() -> None:
    with pytest.raises(KeyError):
        settings_from_env({})


def test_send_form_email_uses_starttls_and_sends() -> None:
    settings = settings_from_env(ENV)
    with mock.patch("fraoverstebenk.mail.smtplib.SMTP") as smtp_class:
        smtp = smtp_class.return_value.__enter__.return_value
        send_form_email(settings, "Bestilling: Solhatt", {"Navn": "Kari", "Telefon": "99887766"})
    smtp_class.assert_called_once_with("smtp.example.com", 587)
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with("bruker", "hemmelig")
    message = smtp.send_message.call_args.args[0]
    assert message["Subject"] == "Bestilling: Solhatt"
    assert message["From"] == "nettside@example.com"
    assert message["To"] == "carl@example.com"
    assert "Navn: Kari" in message.get_content()
    assert "Telefon: 99887766" in message.get_content()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_mail.py -v`
Expected: FAIL with ImportError.

- [ ] **Step 3: Write the implementation**

`src/fraoverstebenk/mail.py`:

```python
from __future__ import annotations

import os
import smtplib
from collections.abc import Mapping
from dataclasses import dataclass
from email.message import EmailMessage


@dataclass(frozen=True)
class MailSettings:
    host: str
    port: int
    username: str
    password: str
    from_addr: str
    to_addr: str


def settings_from_env(env: Mapping[str, str] | None = None) -> MailSettings:
    if env is None:
        env = os.environ
    return MailSettings(
        host=env["SMTP_HOST"],
        port=int(env.get("SMTP_PORT", "587")),
        username=env["SMTP_USERNAME"],
        password=env["SMTP_PASSWORD"],
        from_addr=env["MAIL_FROM"],
        to_addr=env["MAIL_TO"],
    )


def send_form_email(settings: MailSettings, subject: str, fields: dict[str, str]) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.from_addr
    message["To"] = settings.to_addr
    message.set_content("\n".join(f"{label}: {value}" for label, value in fields.items()))
    with smtplib.SMTP(settings.host, settings.port) as smtp:
        smtp.starttls()
        smtp.login(settings.username, settings.password)
        smtp.send_message(message)
```

In `src/fraoverstebenk/app.py`, replace `_mail_not_configured` with the real default sender:

```python
from fraoverstebenk import mail


def _send_mail_from_env(subject: str, fields: dict[str, str]) -> None:
    mail.send_form_email(mail.settings_from_env(), subject, fields)
```

and set `app.config["SEND_MAIL"] = _send_mail_from_env`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest && uv run mypy . && uv run ruff check . && uv run ruff format --check .`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: SMTP mail sending from env config"
```

---

### Task 6: Order form (bestill)

**Files:**
- Modify: `src/fraoverstebenk/components.py`, `src/fraoverstebenk/views.py`
- Test: `tests/test_order_form.py`

**Interfaces:**
- Consumes: `get_hat`, `Hat`, `SEND_MAIL` config, fixtures from `tests/conftest.py` (`client`, `sent_mail`).
- Produces:
  - Components: `form_fields()`, `order_form(hat: Hat, error: str | None = None)`, `thanks()`, `mail_error()`
  - Routes: `GET /hatter/<slug>/bestill`, `POST /hatter/<slug>/bestill`, `GET /takk`
  - Form field names: `navn`, `telefon`, `melding`, honeypot `website`
  - View helper `_read_form() -> dict[str, str] | None` (None = honeypot tripped) reused by Task 7

- [ ] **Step 1: Write the failing tests**

`tests/test_order_form.py`:

```python
from flask.testing import FlaskClient

SentMail = list[tuple[str, dict[str, str]]]


def test_order_form_page(client: FlaskClient) -> None:
    response = client.get("/hatter/solhatt/bestill")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Solhatt" in body
    assert 'name="navn"' in body
    assert 'name="telefon"' in body
    assert 'name="melding"' in body
    assert 'name="website"' in body


def test_order_form_unknown_hat_404(client: FlaskClient) -> None:
    assert client.get("/hatter/finnes-ikke/bestill").status_code == 404


def test_order_submit_sends_mail_and_thanks(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post(
        "/hatter/solhatt/bestill",
        data={"navn": "Kari Nordmann", "telefon": "99887766", "melding": "Størrelse 58"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Takk" in response.get_data(as_text=True)
    assert sent_mail == [
        (
            "Bestilling: Solhatt",
            {"Navn": "Kari Nordmann", "Telefon": "99887766", "Melding": "Størrelse 58"},
        )
    ]


def test_order_submit_honeypot_drops_silently(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post(
        "/hatter/solhatt/bestill",
        data={"navn": "Bot", "telefon": "123", "melding": "", "website": "spam.example"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Takk" in response.get_data(as_text=True)
    assert sent_mail == []


def test_order_submit_requires_name_and_phone(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post(
        "/hatter/solhatt/bestill",
        data={"navn": "", "telefon": "", "melding": "hei"},
    )
    assert response.status_code == 400
    assert "Navn og telefon" in response.get_data(as_text=True)
    assert sent_mail == []


def test_order_submit_mail_failure_shows_error(client: FlaskClient) -> None:
    def broken_mail(subject: str, fields: dict[str, str]) -> None:
        raise ConnectionError("smtp down")

    client.application.config["SEND_MAIL"] = broken_mail
    response = client.post(
        "/hatter/solhatt/bestill",
        data={"navn": "Kari", "telefon": "99887766", "melding": ""},
    )
    assert response.status_code == 500
    assert "beklager" in response.get_data(as_text=True).lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_order_form.py -v`
Expected: FAIL — 404 on the bestill routes.

- [ ] **Step 3: Add form components**

Append to `src/fraoverstebenk/components.py` — extend the htpy import with `button`, `form`, `input`, `label`, `textarea`:

```python
def form_fields() -> list[Element]:
    return [
        p[
            label(for_="navn")["Navn"],
            input("#navn", type="text", name="navn"),
        ],
        p[
            label(for_="telefon")["Telefon"],
            input("#telefon", type="tel", name="telefon"),
        ],
        p[
            label(for_="melding")["Melding"],
            textarea("#melding", name="melding", rows=5),
        ],
        p(".hp", aria_hidden="true")[
            label(for_="website")["Nettside"],
            input("#website", type="text", name="website", tabindex="-1", autocomplete="off"),
        ],
    ]


def order_form(hat: Hat, error: str | None = None) -> Element:
    return layout(
        f"Bestill {hat.title}",
        section[
            h1[f"Bestill {hat.title}"],
            p[hat.subtitle],
            p(".error")[error] if error else None,
            form(method="post")[
                form_fields(),
                p[button(type="submit")["Send bestilling"]],
            ],
        ],
    )


def thanks() -> Element:
    return layout(
        "Takk",
        section[
            h1["Takk!"],
            p["Vi har mottatt meldingen din og tar kontakt så snart vi kan."],
        ],
    )


def mail_error() -> Element:
    return layout(
        "Noe gikk galt",
        section[
            h1["Beklager, noe gikk galt"],
            p["Vi klarte ikke å sende meldingen din akkurat nå. Prøv igjen litt senere."],
        ],
    )
```

- [ ] **Step 4: Add views**

Append to `src/fraoverstebenk/views.py` — add imports `redirect`, `request`, `url_for` from `flask`, `Response` from `werkzeug.wrappers`, `logging`; add `logger = logging.getLogger(__name__)` after the blueprint:

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest && uv run mypy . && uv run ruff check . && uv run ruff format --check .`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: order form with honeypot and mail delivery"
```

---

### Task 7: Contact page and godt-å-vite page

**Files:**
- Modify: `src/fraoverstebenk/components.py`, `src/fraoverstebenk/views.py`
- Test: `tests/test_contact_and_posts.py`

**Interfaces:**
- Consumes: `form_fields`, `layout`, `_read_form`, `_submit`, `load_posts`, `Post`.
- Produces:
  - Components: `contact_page(error: str | None = None)`, `posts_page(posts: list[Post])`
  - Routes: `GET /kontakt`, `POST /kontakt`, `GET /godt-a-vite/`

- [ ] **Step 1: Write the failing tests**

`tests/test_contact_and_posts.py`:

```python
from flask.testing import FlaskClient

SentMail = list[tuple[str, dict[str, str]]]


def test_contact_page(client: FlaskClient) -> None:
    response = client.get("/kontakt")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Kontakt" in body
    assert 'name="navn"' in body
    assert 'name="website"' in body


def test_contact_submit_sends_mail(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post(
        "/kontakt",
        data={"navn": "Ola", "telefon": "12345678", "melding": "Hei!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Takk" in response.get_data(as_text=True)
    assert sent_mail == [
        ("Kontaktskjema", {"Navn": "Ola", "Telefon": "12345678", "Melding": "Hei!"})
    ]


def test_contact_submit_honeypot(client: FlaskClient, sent_mail: SentMail) -> None:
    client.post(
        "/kontakt",
        data={"navn": "Bot", "telefon": "1", "melding": "", "website": "x"},
    )
    assert sent_mail == []


def test_contact_submit_requires_name_and_phone(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post("/kontakt", data={"navn": "", "telefon": ""})
    assert response.status_code == 400
    assert sent_mail == []


def test_posts_page_renders_all_posts(client: FlaskClient) -> None:
    response = client.get("/godt-a-vite/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Godt å vite" in body
    assert "Stell av hatten" in body
    assert "Børst hatten forsiktig." in body
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_contact_and_posts.py -v`
Expected: FAIL — 404 on `/kontakt` and `/godt-a-vite/`.

- [ ] **Step 3: Add components**

Append to `src/fraoverstebenk/components.py` — add `time` to the htpy import and `Post` to the content import:

```python
def contact_page(error: str | None = None) -> Element:
    return layout(
        "Kontakt",
        section[
            h1["Kontakt oss"],
            p["Send oss en melding, så ringer vi deg tilbake."],
            p(".error")[error] if error else None,
            form(method="post")[
                form_fields(),
                p[button(type="submit")["Send melding"]],
            ],
        ],
    )


def posts_page(posts: list[Post]) -> Element:
    return layout(
        "Godt å vite",
        section[
            h1["Godt å vite"],
            [
                article[
                    h2[post.title],
                    time(datetime=post.published.isoformat())[
                        post.published.strftime("%d.%m.%Y")
                    ],
                    div[post.body],
                ]
                for post in posts
            ],
        ],
    )
```

- [ ] **Step 4: Add views**

Append to `src/fraoverstebenk/views.py` — add `load_posts` to the content import:

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest && uv run mypy . && uv run ruff check . && uv run ruff format --check .`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: contact page and godt-å-vite posts page"
```

---

### Task 8: Sample content, stylesheet, placeholder images

**Files:**
- Create: `content/hatter/solhatt.md`, `content/hatter/vinterlue.md`, `content/godt-a-vite/2026-07-01-stell-av-hatten.md`, `static/style.css`, `static/images/hatter/solhatt.svg`, `static/images/hatter/vinterlue.svg`
- Test: `tests/test_real_content.py`

**Interfaces:**
- Consumes: the whole app with `CONTENT_DIR` pointed at the repo's real `content/` directory.

- [ ] **Step 1: Write the failing test**

`tests/test_real_content.py`:

```python
from pathlib import Path

from fraoverstebenk.app import create_app

REPO_ROOT = Path(__file__).parent.parent


def test_real_content_renders() -> None:
    app = create_app({"CONTENT_DIR": REPO_ROOT / "content", "TESTING": True})
    client = app.test_client()
    assert client.get("/").status_code == 200
    overview = client.get("/hatter/").get_data(as_text=True)
    assert "Solhatt" in overview
    detail = client.get("/hatter/solhatt/").status_code
    assert detail == 200
    posts = client.get("/godt-a-vite/").get_data(as_text=True)
    assert "Stell av hatten" in posts


def test_referenced_images_exist() -> None:
    from fraoverstebenk.content import load_hats

    for hat in load_hats(REPO_ROOT / "content"):
        image_path = REPO_ROOT / hat.image.lstrip("/")
        assert image_path.is_file(), f"Mangler bilde: {hat.image}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_real_content.py -v`
Expected: FAIL — no `content/` directory.

- [ ] **Step 3: Create sample content**

`content/hatter/solhatt.md`:

```markdown
---
title: Solhatt
subtitle: Bred brem, kjølig panne
image: /static/images/hatter/solhatt.svg
sort: 1
---
En klassisk solhatt med bred brem. Flettet av naturstrå, lett som en fjær
og perfekt for lange dager på øverste benk.

- Naturstrå
- Innvendig svettebånd
- Størrelse 56–60
```

`content/hatter/vinterlue.md`:

```markdown
---
title: Vinterlue
subtitle: Varm og god
image: /static/images/hatter/vinterlue.svg
sort: 2
---
Strikket vinterlue i myk ull. Holder hodet varmt uansett hvor kaldt det
blir på benken.

- 100 % norsk ull
- Dobbelt brett over ørene
```

`content/godt-a-vite/2026-07-01-stell-av-hatten.md`:

```markdown
---
title: Stell av hatten
date: 2026-07-01
---
Børst hatten forsiktig med en myk børste, og la den tørke i romtemperatur
hvis den blir våt. Aldri på ovnen!
```

`static/images/hatter/solhatt.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150">
  <rect width="200" height="150" fill="#f0e6d2"/>
  <ellipse cx="100" cy="95" rx="70" ry="18" fill="#c9a86a"/>
  <path d="M60 95 Q60 45 100 45 Q140 45 140 95 Z" fill="#d9b97e"/>
  <text x="100" y="135" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7a6a4f">Solhatt</text>
</svg>
```

`static/images/hatter/vinterlue.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150">
  <rect width="200" height="150" fill="#e2e8f0"/>
  <path d="M55 100 Q55 40 100 40 Q145 40 145 100 Z" fill="#8496b0"/>
  <rect x="50" y="95" width="100" height="18" rx="8" fill="#64748b"/>
  <circle cx="100" cy="38" r="8" fill="#cbd5e1"/>
  <text x="100" y="135" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#475569">Vinterlue</text>
</svg>
```

`static/style.css` (minimal neutral stylesheet; real design comes later):

```css
:root {
  font-family: system-ui, sans-serif;
  line-height: 1.6;
}

body {
  margin: 0 auto;
  max-width: 42rem;
  padding: 0 1rem;
}

header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #ddd;
}

nav {
  display: flex;
  gap: 1rem;
}

ul.hats {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr));
  gap: 1rem;
}

ul.hats img,
article img {
  max-width: 100%;
  height: auto;
}

form label {
  display: block;
}

form input,
form textarea {
  width: 100%;
  max-width: 24rem;
}

.hp {
  display: none;
}

.error {
  color: #b00020;
}

footer {
  margin-top: 3rem;
  padding: 1rem 0;
  border-top: 1px solid #ddd;
  color: #666;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest && uv run mypy . && uv run ruff check . && uv run ruff format --check .`
Expected: all pass.

- [ ] **Step 5: Manual smoke test**

Run: `uv run flask --app fraoverstebenk.app:create_app run --port 5001 &` then `curl -s http://127.0.0.1:5001/hatter/ | grep Solhatt` and `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5001/static/style.css`, then kill the server.
Expected: Solhatt in output; 200 for the stylesheet.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: sample content, placeholder images and base stylesheet"
```

---

### Task 9: Docker, compose, env example, README

**Files:**
- Create: `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `.env.example`, `README.md`

**Interfaces:**
- Consumes: gunicorn entrypoint `fraoverstebenk.app:create_app()`, env vars from Task 5.

- [ ] **Step 1: Write Dockerfile and .dockerignore**

`Dockerfile`:

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY src ./src
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm
RUN useradd --create-home app
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY content ./content
COPY static ./static
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "fraoverstebenk.app:create_app()"]
```

`.dockerignore`:

```
.git
.venv
.env
__pycache__
*.pyc
.pytest_cache
.mypy_cache
.ruff_cache
docs
tests
```

- [ ] **Step 2: Write docker-compose.yml**

```yaml
services:
  web:
    build: .
    container_name: fraoverstebenk
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    env_file:
      - .env
    networks:
      - proxy
    volumes:
      - ./content:/app/content:ro
      - ./static:/app/static:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.fraoverstebenk.entrypoints=https"
      - "traefik.http.routers.fraoverstebenk.rule=Host(`xn--fraverstebenk-dnb.no`) || Host(`www.xn--fraverstebenk-dnb.no`)"
      - "traefik.http.routers.fraoverstebenk.tls=true"
      - "traefik.http.routers.fraoverstebenk.tls.certresolver=http"
      - "traefik.http.services.fraoverstebenk.loadbalancer.server.port=8000"

networks:
  proxy:
    external: true
```

- [ ] **Step 3: Write .env.example**

```
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
MAIL_FROM=nettside@fraoverstebenk.example
MAIL_TO=you@example.com
```

- [ ] **Step 4: Write README.md**

````markdown
# fraøverstebenk.no

Nettsiden til «fra øverste benk». Flask + [htpy](https://htpy.dev/), innhold i
markdown, e-post via SMTP. Domenet er et IDN: `fraøverstebenk.no` =
`xn--fraverstebenk-dnb.no` (punycode brukes i Traefik-ruting og TLS-sertifikat).

## Utvikling

Krever [mise](https://mise.jdx.dev/) (installerer python og uv automatisk):

```bash
mise install
uv sync
mise run dev        # utviklingsserver på :5000
mise run check      # test + lint + typecheck
```

## Innhold

Nye hatter: legg en `.md`-fil i `content/hatter/`:

```markdown
---
title: Solhatt
subtitle: Bred brem, kjølig panne
image: /static/images/hatter/solhatt.svg
sort: 1
---
Beskrivelse i markdown.
```

Bildet legges i `static/images/hatter/`. Nye «Godt å vite»-poster: legg en
`.md`-fil i `content/godt-a-vite/` med `title` og `date` i frontmatter.

I produksjon er `content/` og `static/` montert inn i containeren, så nytt
innhold er bare `git pull` på serveren — ingen rebuild.

## Deploy

```bash
cp .env.example .env
# fyll inn SMTP-verdier i .env
docker compose up -d --build
```

Traefik når containeren over det eksterne `proxy`-nettverket; ingen porter
publiseres. Ved kodeendringer: `git pull && docker compose up -d --build`.
````

- [ ] **Step 5: Verify**

Run: `uv lock --check && uv run pytest && uv run mypy . && uv run ruff check .`
Expected: lockfile up to date, everything green.

If Docker is available locally, also run: `docker build -t fraoverstebenk-test .` and expect a successful build; then `docker compose config -q` to validate the compose file. If Docker is not available, note it and move on — the compose file matches the server's Traefik setup.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: Dockerfile, compose with Traefik labels, deploy docs"
```
