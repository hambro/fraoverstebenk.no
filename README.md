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
title: Solnedgang
meta: no. 014 · gradient, prikket · 1 190 kr
accent: "#FF4E2E"
image: /static/images/hatter/solnedgang.svg
photo: /static/images/hatter/foto-solnedgang.png
sort: 1
---
Beskrivelse i markdown.
```

`meta`, `accent` og `photo` er valgfrie. `image` vises i galleriet (rund
utsnitt), `photo` («slik ser den ut i virkeligheten») vises på
bestillingssiden når den finnes. Bilder legges i `static/images/hatter/`.

Nye «Fra benken»-poster: legg en `.md`-fil i `content/fra-benken/` med
`title` og `date` i frontmatter. Valgfritt: `tag` (etikett på kortet),
`color` (fargeprikk) og `teaser` (utdraget på oversikten).

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
