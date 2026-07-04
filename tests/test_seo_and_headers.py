import json

from flask.testing import FlaskClient


def test_frontpage_has_seo_head(client: FlaskClient) -> None:
    body = client.get("/").get_data(as_text=True)
    assert '<meta name="description" content="Håndfiltede badstuhatter i ull' in body
    assert '<link rel="canonical" href="https://xn--fraverstebenk-dnb.no/">' in body
    assert '<meta property="og:title"' in body
    assert '<meta property="og:image" content="https://xn--fraverstebenk-dnb.no/static/' in body
    assert '<meta property="og:locale" content="nb_NO">' in body
    assert 'name="robots"' not in body


def test_order_page_has_product_json_ld(client: FlaskClient) -> None:
    body = client.get("/hatter/solnedgang/bestill").get_data(as_text=True)
    assert '<script type="application/ld+json">' in body
    start = body.index('<script type="application/ld+json">') + len(
        '<script type="application/ld+json">'
    )
    data = json.loads(body[start : body.index("</script>", start)])
    assert data["@type"] == "Product"
    assert data["name"] == "Solnedgang"
    assert data["offers"]["price"] == "1190"
    assert data["offers"]["priceCurrency"] == "NOK"


def test_post_page_has_article_json_ld(client: FlaskClient) -> None:
    body = client.get("/fra-benken/stell-av-hatten/").get_data(as_text=True)
    assert '"@type": "Article"' in body
    assert '"headline": "Stell av hatten"' in body
    assert '<meta property="og:type" content="article">' in body


def test_thanks_page_is_noindex(client: FlaskClient) -> None:
    body = client.get("/takk").get_data(as_text=True)
    assert '<meta name="robots" content="noindex">' in body


def test_robots_txt(client: FlaskClient) -> None:
    response = client.get("/robots.txt")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "Sitemap: https://xn--fraverstebenk-dnb.no/sitemap.xml" in body


def test_sitemap_lists_all_pages(client: FlaskClient) -> None:
    response = client.get("/sitemap.xml")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    for path in ["/", "/hatter/", "/fra-benken/", "/kontakt"]:
        assert f"<loc>https://xn--fraverstebenk-dnb.no{path}</loc>" in body
    assert "<loc>https://xn--fraverstebenk-dnb.no/hatter/solnedgang/bestill</loc>" in body
    assert (
        "<url><loc>https://xn--fraverstebenk-dnb.no/fra-benken/stell-av-hatten/</loc>"
        "<lastmod>2026-06-01</lastmod></url>" in body
    )


def test_404_page_is_styled(client: FlaskClient) -> None:
    response = client.get("/finnes-ikke")
    body = response.get_data(as_text=True)
    assert response.status_code == 404
    assert "Denne benken finnes ikke" in body
    assert "<style>" in body
    assert '<meta name="robots" content="noindex">' in body


def test_security_headers(client: FlaskClient) -> None:
    headers = client.get("/").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert headers["Strict-Transport-Security"] == "max-age=31536000"
    assert "default-src 'none'" in headers["Content-Security-Policy"]
    assert "style-src 'self' 'unsafe-inline'" in headers["Content-Security-Policy"]


def test_static_assets_get_long_cache(client: FlaskClient) -> None:
    response = client.get("/static/fonts/fredoka-latin.woff2")
    assert response.headers["Cache-Control"] == "public, max-age=2592000"
    css = client.get("/static/style.css")
    assert css.headers["Cache-Control"] == "public, max-age=3600"


def test_skip_link_and_aria_current(client: FlaskClient) -> None:
    body = client.get("/hatter/").get_data(as_text=True)
    assert '<a class="skip-link" href="#innhold">' in body
    assert '<main id="innhold">' in body
    assert 'aria-current="page"' in body
