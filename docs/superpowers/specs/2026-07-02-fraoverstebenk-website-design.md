# fraøverstebenk.no — Website Design

Date: 2026-07-02
Status: Approved

## Purpose

A small Norwegian-language website for "fra øverste benk": a hat shop with a
handful of products, short blog-style posts, and two forms (order + contact)
that email the owner. No payments, no database, no admin UI.

The domain is an IDN: fraøverstebenk.no, which resolves as
`xn--fraverstebenk-dnb.no`. Routing and TLS must use the punycode name.

## Stack

- Python 3.13
- Flask + htpy (all HTML as typed Python; no template files)
- python-frontmatter + markdown for content parsing
- stdlib smtplib for email
- gunicorn in the container
- Tooling: mise (pins python + uv), uv (deps/venv), ruff (lint + format),
  mypy (strict), pytest

## Content model

Content lives in markdown files with YAML frontmatter. Adding a hat or post
is dropping a `.md` file in a folder — no Python edits.

```
content/
  hatter/<slug>.md
      frontmatter: title, subtitle, image, sort
      body: description (markdown)
  godt-a-vite/YYYY-MM-DD-<slug>.md
      frontmatter: title, date
      body: post (markdown)
static/images/hatter/    # hat photos, referenced from frontmatter `image`
```

Markdown is read and parsed per request. At ≤10 hats and a handful of posts
this costs ~1ms and means new content appears immediately (content is
bind-mounted in production). No caching or invalidation logic.

## Application layout

```
src/fraoverstebenk/
  app.py          # Flask app factory, config from env
  views.py        # routes
  components.py   # htpy layout + shared components
  content.py      # markdown loading/parsing → Hat / Post dataclasses
  mail.py         # SMTP send, config via env vars
tests/
Dockerfile, docker-compose.yml, mise.toml, pyproject.toml
```

## Routes

| Route | Page |
|---|---|
| `/` | Frontpage |
| `/hatter/` | "Kaldt hode kolleksjon" — grid of hats (title, subtitle, photo) |
| `/hatter/<slug>/` | Hat details (title, subtitle, photo, description) + buy button leading to order form |
| `/hatter/<slug>/bestill` | GET: order form (name, phone, message). POST: send email, show thank-you |
| `/godt-a-vite/` | All posts rendered in full on one page (they are short) |
| `/kontakt` | GET: contact form (name, phone, message). POST: send email, show thank-you |

Unknown hat slugs return 404.

## Email

- Plain SMTP with TLS via env vars: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`,
  `SMTP_PASSWORD`, `MAIL_FROM`, `MAIL_TO`.
- `.env` is git-ignored; a `.env.example` documents every variable.
- Both forms include a hidden honeypot field; submissions that fill it are
  silently dropped (bot spam).
- If SMTP fails, the user sees a polite error page and the submission is
  written to the application log so nothing is silently lost.

## Docker / Traefik

- Multi-stage Dockerfile: uv builds the venv, slim Python runtime image,
  non-root user, gunicorn on port 8000.
- No published ports; Traefik reaches the container over the external
  `proxy` network.
- Traefik labels route the punycode host:

```yaml
- "traefik.enable=true"
- "traefik.http.routers.fraoverstebenk.entrypoints=https"
- "traefik.http.routers.fraoverstebenk.rule=Host(`xn--fraverstebenk-dnb.no`) || Host(`www.xn--fraverstebenk-dnb.no`)"
- "traefik.http.routers.fraoverstebenk.tls=true"
- "traefik.http.routers.fraoverstebenk.tls.certresolver=http"
```

- Let's Encrypt issues certs for the punycode name; browsers display
  fraøverstebenk.no.
- Deploy: `git pull && docker compose up -d --build` on the server (build on
  server, no registry).
- `./content` and `./static` are bind-mounted so new content is `git pull`
  alone, no rebuild.

## Testing

pytest with Flask's test client:

- Every page returns 200 and contains expected content.
- Markdown parsing handles the frontmatter schema (and rejects/skips
  malformed files without crashing the site).
- Form POSTs send mail (SMTP mocked) and render the thank-you page.
- Honeypot submissions are dropped and send no mail.
- Unknown hat slug → 404.

## Out of scope

- Design/styling decisions: pages ship semantic HTML with a minimal neutral
  stylesheet to be replaced later.
- Payments, inventory, database, admin UI, analytics.
- Localization beyond Norwegian.
