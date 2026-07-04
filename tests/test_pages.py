from flask.testing import FlaskClient


def test_frontpage(client: FlaskClient) -> None:
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Fra øverste benk" in body
    assert "Håndfiltede badstuhatter, én og én." in body
    assert "Se hattene" in body


def test_layout_links_stylesheet_and_logo(client: FlaskClient) -> None:
    body = client.get("/").get_data(as_text=True)
    assert '"/static/style.css"' in body
    assert "/static/images/logo-flame.png" in body


def test_nav_marks_active_page(client: FlaskClient) -> None:
    body = client.get("/hatter/").get_data(as_text=True)
    assert '<a class="active" href="/hatter/" aria-current="page">Hattene</a>' in body


def test_hat_overview_shows_hats(client: FlaskClient) -> None:
    response = client.get("/hatter/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Hattene" in body
    assert "Solnedgang" in body
    assert "no. 014 · gradient, prikket · 1 190 kr" in body
    assert "/static/images/hatter/solnedgang.svg" in body
    assert "/hatter/solnedgang/bestill" in body
    assert "01 modeller" in body
    assert "Lyst på dine egne farger?" in body
    assert "Håndlaget i Norge, én om gangen." in body
