from __future__ import annotations

from htpy import (
    Element,
    Node,
    a,
    article,
    body,
    button,
    div,
    footer,
    form,
    h1,
    h2,
    h3,
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
    section,
    textarea,
    time,
    title,
    ul,
)

from fraoverstebenk.content import Hat, Post

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
                    time(datetime=post.published.isoformat())[post.published.strftime("%d.%m.%Y")],
                    div[post.body],
                ]
                for post in posts
            ],
        ],
    )
