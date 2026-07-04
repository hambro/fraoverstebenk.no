from flask.testing import FlaskClient


def test_contact_page_has_mailto_and_cards(client: FlaskClient) -> None:
    response = client.get("/kontakt")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Kontakt" in body
    assert "mailto:hei@fraoverstebenk.no" in body
    assert "Bestill i dine farger" in body
    assert "Stell av hatten" in body
    assert "Tips til kartet" in body


def test_posts_page_shows_teaser_cards(client: FlaskClient) -> None:
    response = client.get("/fra-benken/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Fra benken" in body
    assert "Stell av hatten" in body
    assert "Slik holder hatten seg fin i mange år." in body
    assert "tips og triks" in body
    assert "/fra-benken/stell-av-hatten/" in body
    assert "Børst hatten forsiktig." not in body


def test_post_detail_shows_body(client: FlaskClient) -> None:
    response = client.get("/fra-benken/stell-av-hatten/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Stell av hatten" in body
    assert "Børst hatten forsiktig." in body


def test_post_detail_unknown_slug_404(client: FlaskClient) -> None:
    assert client.get("/fra-benken/finnes-ikke/").status_code == 404


def test_old_posts_url_redirects(client: FlaskClient) -> None:
    response = client.get("/godt-a-vite/")
    assert response.status_code == 301
    assert response.headers["Location"].endswith("/fra-benken/")
