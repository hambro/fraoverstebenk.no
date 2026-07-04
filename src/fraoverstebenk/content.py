from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from pathlib import Path

import frontmatter
import markdown
from markupsafe import Markup

logger = logging.getLogger(__name__)

DEFAULT_ACCENT = "#FF4E2E"


@dataclass(frozen=True)
class Hat:
    slug: str
    title: str
    meta: str
    accent: str
    image: str
    photo: str | None
    sort: int
    description: Markup


def _render_markdown(text: str) -> Markup:
    return Markup(markdown.markdown(text))


def _load_hat(path: Path) -> Hat | None:
    try:
        parsed = frontmatter.load(path)
        photo = parsed.get("photo")
        return Hat(
            slug=path.stem,
            title=str(parsed["title"]),
            meta=str(parsed.get("meta", "")),
            accent=str(parsed.get("accent", DEFAULT_ACCENT)),
            image=str(parsed["image"]),
            photo=str(photo) if photo else None,
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


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    tag: str
    color: str
    teaser: str
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
            tag=str(parsed.get("tag", "")),
            color=str(parsed.get("color", DEFAULT_ACCENT)),
            teaser=str(parsed.get("teaser", "")),
            published=published,
            body=_render_markdown(parsed.content),
        )
    except (KeyError, ValueError) as error:
        logger.warning("Hopper over %s: %s", path, error)
        return None


def load_posts(content_dir: Path) -> list[Post]:
    posts = [
        post
        for path in sorted((content_dir / "fra-benken").glob("*.md"))
        if (post := _load_post(path)) is not None
    ]
    return sorted(posts, key=lambda post: post.published, reverse=True)


def get_post(content_dir: Path, slug: str) -> Post | None:
    for post in load_posts(content_dir):
        if post.slug == slug:
            return post
    return None
