from pathlib import Path

import pytest

from fraoverstebenk.content import get_hat, load_hats, load_posts


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
