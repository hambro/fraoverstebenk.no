from flask.testing import FlaskClient


def test_frontpage(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "fra øverste benk" in response.get_data(as_text=True)


def test_layout_links_stylesheets(client: FlaskClient) -> None:
    body = client.get("/").get_data(as_text=True)
    assert '"/static/pico.classless.min.css"' in body
    assert '"/static/style.css"' in body


def test_hat_overview_shows_hats(client: FlaskClient) -> None:
    response = client.get("/hatter/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Kaldt hode kolleksjon" in body
    assert "Solhatt" in body
    assert "Bred brem mot sol" in body
    assert "/static/images/hatter/solhatt.svg" in body
    assert "/hatter/solhatt/" in body


def test_hat_detail(client: FlaskClient) -> None:
    response = client.get("/hatter/solhatt/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Solhatt" in body
    assert "<strong>bred brem</strong>" in body
    assert "/hatter/solhatt/bestill" in body


def test_hat_detail_unknown_slug_404(client: FlaskClient) -> None:
    assert client.get("/hatter/finnes-ikke/").status_code == 404
