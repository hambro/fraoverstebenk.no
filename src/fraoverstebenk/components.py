from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from htpy import (
    Element,
    Node,
    a,
    body,
    button,
    div,
    footer,
    form,
    h1,
    h2,
    head,
    header,
    html,
    img,
    input,
    label,
    li,
    link,
    main,
    meta,
    nav,
    p,
    script,
    section,
    span,
    style,
    textarea,
    time,
    title,
    ul,
)
from markupsafe import Markup

from fraoverstebenk.content import Hat, Post

SITE_NAME = "Fra øverste benk"
CONTACT_EMAIL = "hei@fraoverstebenk.no"
BASE_URL = "https://xn--fraverstebenk-dnb.no"
DEFAULT_OG_IMAGE = "/static/images/logo-flame.png"

NAV_ITEMS = [
    ("hattene", "/hatter/", "Hattene"),
    ("fra-benken", "/fra-benken/", "Fra benken"),
    ("kontakt", "/kontakt", "Kontakt"),
]

CRAFT_STEPS = [
    (
        "#FFB01F",
        "Legge ull",
        "Løs, farget ull legges lag på lag over en form — det er her gradienter og "
        "prikker plasseres.",
    ),
    (
        "#FF4E2E",
        "Filte",
        "Såpe, varmt vann og hundrevis av håndbevegelser gjør ulla tett og sammenhengende.",
    ),
    (
        "#43B54A",
        "Forme",
        "Hatten formes og tørkes til den holder fasongen — klar for mange timer på øverste benk.",
    ),
]


def _brand() -> Element:
    return a(".brand", href="/")[
        img(src="/static/images/logo-flame.png", alt=""),
        span[SITE_NAME],
    ]


def _plain_text(rendered: Markup) -> str:
    return re.sub(r"<[^>]+>", "", str(rendered)).strip()


def _json_ld(data: dict[str, Any]) -> Element:
    return script(type="application/ld+json")[Markup(json.dumps(data, ensure_ascii=False))]


def _inline_css() -> Markup:
    return Markup(Path("static/style.css").read_text(encoding="utf-8"))


def _nav_link(href: str, label_: str, is_active: bool) -> Element:
    if is_active:
        return a(".active", href=href, aria_current="page")[label_]
    return a(href=href)[label_]


def _nav(active: str | None) -> Element:
    return nav(".site-nav")[
        _brand(),
        div(".nav-links")[
            [_nav_link(href, label_, key == active) for key, href, label_ in NAV_ITEMS]
        ],
    ]


def _simple_footer(narrow: bool = False) -> Element:
    return footer(".site-footer.narrow" if narrow else ".site-footer")[
        span(".brand-name")[SITE_NAME],
        span(".mono")["© 2026 · håndfiltet i norge"],
    ]


def _rich_footer() -> Element:
    return footer(".site-footer.rich")[
        div(".footer-left")[
            span(".brand-name")[SITE_NAME],
            span(".footer-tagline")[
                "Lyst på en hatt i dine farger? Send oss en melding — vi filter på bestilling."
            ],
        ],
        div(".footer-right")[
            a(".link-dotted", href=f"mailto:{CONTACT_EMAIL}")[CONTACT_EMAIL],
            span(".mono")["© 2026 · håndfiltet i norge"],
        ],
    ]


def layout(
    page_title: str,
    content: Node,
    *,
    description: str,
    path: str,
    active: str | None = None,
    page_footer: Node | None = None,
    og_type: str = "website",
    og_image: str = DEFAULT_OG_IMAGE,
    head_extra: Node = None,
    noindex: bool = False,
) -> Element:
    return html(lang="no")[
        head[
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            title[f"{page_title} – {SITE_NAME}"],
            meta(name="description", content=description),
            meta(name="robots", content="noindex") if noindex else None,
            link(rel="canonical", href=f"{BASE_URL}{path}"),
            meta(property="og:site_name", content=SITE_NAME),
            meta(property="og:locale", content="nb_NO"),
            meta(property="og:type", content=og_type),
            meta(property="og:title", content=page_title),
            meta(property="og:description", content=description),
            meta(property="og:url", content=f"{BASE_URL}{path}"),
            meta(property="og:image", content=f"{BASE_URL}{og_image}"),
            link(rel="icon", href="/static/images/logo-flame.png", type="image/png"),
            style[_inline_css()],
            head_extra,
        ],
        body[
            a(".skip-link", href="#innhold")["Hopp til innhold"],
            header[_nav(active)],
            main("#innhold")[content],
            page_footer if page_footer is not None else _simple_footer(),
        ],
    ]


def frontpage(hero_image: str | None = None) -> Element:
    return layout(
        "Håndfiltede badstuhatter",
        description=(
            "Håndfiltede badstuhatter i ull, filtet for hånd i Norge. "
            "Ingen blir like — din finnes det bare én av."
        ),
        path="/",
        content=section(".hero.container-wide")[
            div(".hero-text")[
                h1["Håndfiltede badstuhatter, én og én."],
                p(".lead")[
                    "Hver hatt er filtet for hånd i Norge — av ull, såpe og varmt vann. "
                    "Ingen blir like. Din finnes det bare én av."
                ],
                div(".hero-actions")[
                    a(".btn", href="/hatter/")["Se hattene"],
                    a(".link-dotted", href="/fra-benken/")["Fra benken"],
                ],
            ],
            div(".hero-image")[
                span(".dot.dot-sun"),
                span(".dot.dot-green"),
                span(".dot.dot-accent"),
                img(
                    src=hero_image or "/static/images/hatter/solnedgang.svg",
                    alt="Håndfiltet badstuhatt",
                    fetchpriority="high",
                ),
            ],
        ],
        page_footer=_rich_footer(),
    )


def hat_card(hat: Hat) -> Element:
    return li(".hat-card")[
        div(".hat-circle")[img(src=hat.image, alt=hat.title)],
        div(".hat-info")[
            div(".hat-title-row")[
                span(".hat-name")[hat.title],
                span(".accent-dot", style=f"background: {hat.accent};"),
            ],
            div(".mono")[hat.meta],
            div(".hat-desc")[hat.description],
            a(
                ".btn.order-btn",
                href=f"/hatter/{hat.slug}/bestill",
                style=f"--btn-bg: {hat.accent};",
            )["Bestill denne"],
        ],
    ]


def hat_overview(hats: list[Hat]) -> Element:
    return layout(
        "Hattene",
        description=(
            "Fire fargestemninger, filtet for hånd i Norge. Hver hatt er unik — "
            "velg din, eller bestill i dine egne farger."
        ),
        path="/hatter/",
        content=[
            header(".page-header.container-wide")[
                h1["Hattene"],
                p(".lead")[
                    "Fire fargestemninger, filtet for hånd i Norge. Hver hatt er sin egen — "
                    "fargene legges i ulla der og da, så din blir aldri helt lik bildene."
                ],
            ],
            section(".container-wide.gallery")[
                div(".gallery-meta")[
                    span(".mono")["alle unike · 100% ull · filtet for hånd"],
                    span(".mono")[f"{len(hats):02d} modeller"],
                ],
                ul(".hats")[[hat_card(hat) for hat in hats]],
            ],
            section(".band")[
                div(".container-wide.cta-row")[
                    div(".cta-text")[
                        h2["Lyst på dine egne farger?"],
                        p[
                            "Vi filter på bestilling — velg farger, gradient og prikker, "
                            "så lager vi en hatt som bare finnes én av."
                        ],
                    ],
                    a(".btn", href="/kontakt")["Ta kontakt"],
                ]
            ],
            section(".band.band-light")[
                div(".container-wide.craft")[
                    div(".craft-intro")[
                        h2["Håndlaget i Norge, én om gangen."],
                        p[
                            "Hver hatt starter som løs, farget ull og filtes for hånd — "
                            "lag på lag, til den er tett, varm og formfast. Fargene legges "
                            "der og da, så ingen to hatter blir like."
                        ],
                    ],
                    div(".steps")[
                        [
                            div(".step-card")[
                                span(".step-number", style=f"background: {color};")[str(n)],
                                div(".step-title")[step_title],
                                div(".step-text")[text],
                            ]
                            for n, (color, step_title, text) in enumerate(CRAFT_STEPS, start=1)
                        ]
                    ],
                ]
            ],
        ],
        active="hattene",
    )


def form_fields() -> list[Element]:
    return [
        label(for_="navn")[
            "Navn",
            input("#navn", type="text", name="navn", placeholder="Ditt navn"),
        ],
        label(for_="kontakt")[
            "Telefon eller e-post",
            input("#kontakt", type="text", name="kontakt", placeholder="Så vi kan nå deg"),
        ],
        label(for_="melding")[
            "Beskjed",
            textarea(
                "#melding",
                name="melding",
                rows=3,
                placeholder="Ønsker du andre farger, størrelse eller noe annet?",
            ),
        ],
        p(".hp", aria_hidden="true")[
            label(for_="website")["Nettside"],
            input("#website", type="text", name="website", tabindex="-1", autocomplete="off"),
        ],
    ]


def _product_json_ld(hat: Hat) -> Element:
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": hat.title,
        "description": _plain_text(hat.description),
        "image": BASE_URL + (hat.photo or hat.image),
        "url": f"{BASE_URL}/hatter/{hat.slug}/bestill",
    }
    if hat.price is not None:
        data["offers"] = {
            "@type": "Offer",
            "price": str(hat.price),
            "priceCurrency": "NOK",
            "availability": "https://schema.org/MadeToOrder",
        }
    return _json_ld(data)


def order_form(hat: Hat, error: str | None = None) -> Element:
    return layout(
        f"Bestill {hat.title}",
        description=f"Bestill {hat.title} — håndfiltet badstuhatt i ull. "
        + _plain_text(hat.description),
        path=f"/hatter/{hat.slug}/bestill",
        og_type="product",
        og_image=hat.photo or hat.image,
        head_extra=_product_json_ld(hat),
        content=section(".container-wide.order")[
            span(".mono")[f"bestilling · {hat.meta}"],
            div(".order-grid")[
                div(".order-image")[
                    span(".mono")["slik ser den ut i virkeligheten"],
                    img(src=hat.photo or hat.image, alt=hat.title, fetchpriority="high"),
                ],
                div(".order-details")[
                    div(".hat-title-row")[
                        h1[hat.title],
                        span(".accent-dot.large", style=f"background: {hat.accent};"),
                    ],
                    div(".hat-desc")[hat.description],
                    p[
                        "Hver hatt filtes for hånd på bestilling — din blir sin egen "
                        "variant av denne stemningen."
                    ],
                    p(".error", role="alert")[error] if error else None,
                    form(".order-form", method="post")[
                        form_fields(),
                        button(".btn", type="submit")["Send bestilling"],
                    ],
                ],
            ],
        ],
        active="hattene",
    )


def thanks() -> Element:
    return layout(
        "Takk",
        description="Vi har mottatt meldingen din.",
        path="/takk",
        noindex=True,
        content=section(".container-narrow")[
            div(".confirm-card")[
                span(".check")["✓"],
                div(".confirm-title")["Takk!"],
                div(".confirm-text")[
                    "Vi har mottatt meldingen din og tar kontakt for å avtale farger og levering."
                ],
                a(".link-dotted", href="/hatter/")["Tilbake til hattene"],
            ]
        ],
    )


def mail_error() -> Element:
    return layout(
        "Noe gikk galt",
        description="Meldingen kunne ikke sendes.",
        path="/",
        noindex=True,
        content=section(".container-narrow.post")[
            h1["Beklager, noe gikk galt"],
            p(".lead")["Vi klarte ikke å sende meldingen din akkurat nå. Prøv igjen litt senere."],
        ],
    )


def not_found() -> Element:
    return layout(
        "Siden finnes ikke",
        description="Denne siden finnes ikke.",
        path="/",
        noindex=True,
        content=section(".container-narrow.post")[
            span(".mono")["404"],
            h1["Denne benken finnes ikke"],
            p(".lead")[
                "Siden du leter etter er borte — kanskje den er ute og kjøler seg ned. "
                "Prøv hattene eller forsiden i stedet."
            ],
            div(".hero-actions")[
                a(".btn", href="/hatter/")["Se hattene"],
                a(".link-dotted", href="/")["Til forsiden"],
            ],
        ],
    )


def contact_page() -> Element:
    return layout(
        "Kontakt",
        description=(
            "Spørsmål, bestilling eller badstuprat? Send oss en melding — "
            "vi svarer som regel samme kveld."
        ),
        path="/kontakt",
        content=[
            header(".page-header.container-narrow")[
                h1["Kontakt"],
                p(".lead")[
                    "Spørsmål, bestilling eller bare lyst til å prate badstu? Send en melding "
                    "— vi svarer som regel samme kveld, gjerne fra benken."
                ],
                a(".btn", href=f"mailto:{CONTACT_EMAIL}")[CONTACT_EMAIL],
            ],
            section(".container-narrow.info-cards")[
                div(".info-card")[
                    span(".accent-dot", style="background: #FFB01F;"),
                    div(".card-title")["Bestill i dine farger"],
                    div(".card-text")[
                        "Velg farger, gradient og prikker — vi filter en hatt som bare finnes "
                        "én av. Levering vanligvis innen 2–3 uker."
                    ],
                ],
                div(".info-card")[
                    span(".accent-dot", style="background: #43B54A;"),
                    div(".card-title")["Stell av hatten"],
                    div(".card-text")[
                        "Lurer du på vask, tørking eller lagring? Spør oss — filtet ull er mer "
                        "hardfør enn du tror."
                    ],
                ],
                div(".info-card")[
                    span(".accent-dot", style="background: #3B8DE8;"),
                    div(".card-title")["Tips til kartet"],
                    div(".card-text")[
                        "Kjenner du en badstue eller kulp som fortjener en plass på kartet "
                        "vårt? Vi tar gjerne imot tips."
                    ],
                ],
            ],
        ],
        active="kontakt",
        page_footer=_simple_footer(narrow=True),
    )


def post_card(post: Post) -> Element:
    return a(".post-card", href=f"/fra-benken/{post.slug}/")[
        span(".post-tag.mono")[
            span(".accent-dot.small", style=f"background: {post.color};"),
            post.tag,
        ],
        span(".post-title")[post.title],
        span(".post-teaser")[post.teaser],
        span(".read-more", style=f"border-bottom-color: {post.color};")["Les mer"],
    ]


def posts_page(posts: list[Post]) -> Element:
    return layout(
        "Fra benken",
        description=(
            "Notater fra badstulivet — tips, spørsmål og svar, og steder vi liker. "
            "Skrevet fra øverste benk."
        ),
        path="/fra-benken/",
        content=[
            header(".page-header.container-narrow")[
                h1["Fra benken"],
                p(".lead")[
                    "Notater fra badstulivet — tips, spørsmål og svar, og steder vi liker. "
                    "Skrevet fra øverste benk."
                ],
            ],
            section(".container-narrow.posts")[
                [post_card(post) for post in posts],
                div(".mono.posts-note")["flere notater kommer — tips oss gjerne om temaer"],
            ],
        ],
        active="fra-benken",
        page_footer=_simple_footer(narrow=True),
    )


def _article_json_ld(post: Post) -> Element:
    return _json_ld(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": post.title,
            "description": post.teaser or _plain_text(post.body)[:160],
            "datePublished": post.published.isoformat(),
            "inLanguage": "nb",
            "author": {"@type": "Organization", "name": SITE_NAME},
            "publisher": {"@type": "Organization", "name": SITE_NAME},
            "mainEntityOfPage": f"{BASE_URL}/fra-benken/{post.slug}/",
        }
    )


def post_page(post: Post) -> Element:
    return layout(
        post.title,
        description=post.teaser or _plain_text(post.body)[:160],
        path=f"/fra-benken/{post.slug}/",
        og_type="article",
        head_extra=_article_json_ld(post),
        content=section(".container-narrow.post")[
            span(".post-tag.mono")[
                span(".accent-dot.small", style=f"background: {post.color};"),
                post.tag,
            ],
            h1[post.title],
            time(".mono", datetime=post.published.isoformat())[post.published.strftime("%d.%m.%Y")],
            div(".prose")[post.body],
            p[a(".link-dotted", href="/fra-benken/")["← Fra benken"]],
        ],
        active="fra-benken",
        page_footer=_simple_footer(narrow=True),
    )
