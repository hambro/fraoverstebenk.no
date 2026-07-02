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
