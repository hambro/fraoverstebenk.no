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
            sort=int(str(parsed.get("sort", 0))),
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
