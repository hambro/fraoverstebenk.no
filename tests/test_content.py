from pathlib import Path

import pytest

from fraoverstebenk.content import get_hat, get_post, load_hats, load_posts


def write_hat(content_dir: Path, slug: str, body: str) -> None:
    hat_dir = content_dir / "hatter"
    hat_dir.mkdir(parents=True, exist_ok=True)
    (hat_dir / f"{slug}.md").write_text(body, encoding="utf-8")


GRANSKOG = """---
title: Granskog
meta: no. 015 · gradient, prikket · 1 190 kr
accent: "#43B54A"
image: /static/images/hatter/granskog.svg
photo: /static/images/hatter/foto-granskog.png
sort: 2
---
Mørk **granskoggrønn** med lysegrønne prikker.
"""

SOLNEDGANG = """---
title: Solnedgang
image: /static/images/hatter/solnedgang.svg
sort: 1
---
Gul topp over dyp rød.
"""


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    write_hat(tmp_path, "granskog", GRANSKOG)
    write_hat(tmp_path, "solnedgang", SOLNEDGANG)
    return tmp_path


def test_load_hats_parses_frontmatter_and_body(content_dir: Path) -> None:
    hats = load_hats(content_dir)
    assert [hat.slug for hat in hats] == ["solnedgang", "granskog"]
    granskog = hats[1]
    assert granskog.title == "Granskog"
    assert granskog.meta == "no. 015 · gradient, prikket · 1 190 kr"
    assert granskog.accent == "#43B54A"
    assert granskog.image == "/static/images/hatter/granskog.svg"
    assert granskog.photo == "/static/images/hatter/foto-granskog.png"
    assert "<strong>granskoggrønn</strong>" in str(granskog.description)


def test_hat_defaults_for_optional_fields(content_dir: Path) -> None:
    hat = get_hat(content_dir, "solnedgang")
    assert hat is not None
    assert hat.meta == ""
    assert hat.accent == "#FF4E2E"
    assert hat.photo is None


def test_load_hats_skips_malformed_files(content_dir: Path) -> None:
    write_hat(content_dir, "broken", "---\nmeta: mangler tittel\n---\nMangler resten.\n")
    hats = load_hats(content_dir)
    assert [hat.slug for hat in hats] == ["solnedgang", "granskog"]


def test_load_hats_with_missing_directory(tmp_path: Path) -> None:
    assert load_hats(tmp_path) == []


def test_get_hat_by_slug(content_dir: Path) -> None:
    hat = get_hat(content_dir, "granskog")
    assert hat is not None
    assert hat.title == "Granskog"


def test_get_hat_unknown_slug(content_dir: Path) -> None:
    assert get_hat(content_dir, "finnes-ikke") is None


def write_post(content_dir: Path, filename: str, body: str) -> None:
    post_dir = content_dir / "fra-benken"
    post_dir.mkdir(parents=True, exist_ok=True)
    (post_dir / filename).write_text(body, encoding="utf-8")


STELL = """---
title: Stell av hatten
date: 2026-06-01
tag: tips og triks
color: "#43B54A"
teaser: Slik holder hatten seg fin.
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
    write_post(tmp_path, "stell.md", STELL)
    write_post(tmp_path, "storrelse.md", STORRELSE)
    posts = load_posts(tmp_path)
    assert [post.title for post in posts] == ["Finn riktig størrelse", "Stell av hatten"]
    stell = posts[1]
    assert stell.tag == "tips og triks"
    assert stell.color == "#43B54A"
    assert stell.teaser == "Slik holder hatten seg fin."
    assert "<em>forsiktig</em>" in str(stell.body)


def test_post_defaults_for_optional_fields(tmp_path: Path) -> None:
    write_post(tmp_path, "storrelse.md", STORRELSE)
    post = get_post(tmp_path, "storrelse")
    assert post is not None
    assert post.tag == ""
    assert post.color == "#FF4E2E"
    assert post.teaser == ""


def test_load_posts_skips_malformed(tmp_path: Path) -> None:
    write_post(tmp_path, "stell.md", STELL)
    write_post(tmp_path, "ugyldig.md", "---\ntitle: Uten dato\n---\nHei.\n")
    posts = load_posts(tmp_path)
    assert [post.title for post in posts] == ["Stell av hatten"]


def test_load_posts_with_missing_directory(tmp_path: Path) -> None:
    assert load_posts(tmp_path) == []


def test_get_post_unknown_slug(tmp_path: Path) -> None:
    write_post(tmp_path, "stell.md", STELL)
    assert get_post(tmp_path, "finnes-ikke") is None
