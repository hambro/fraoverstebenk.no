from flask.testing import FlaskClient

SentMail = list[tuple[str, dict[str, str]]]


def test_order_form_page(client: FlaskClient) -> None:
    response = client.get("/hatter/solhatt/bestill")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Solhatt" in body
    assert 'name="navn"' in body
    assert 'name="telefon"' in body
    assert 'name="melding"' in body
    assert 'name="website"' in body


def test_order_form_unknown_hat_404(client: FlaskClient) -> None:
    assert client.get("/hatter/finnes-ikke/bestill").status_code == 404


def test_order_submit_sends_mail_and_thanks(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post(
        "/hatter/solhatt/bestill",
        data={"navn": "Kari Nordmann", "telefon": "99887766", "melding": "Størrelse 58"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Takk" in response.get_data(as_text=True)
    assert sent_mail == [
        (
            "Bestilling: Solhatt",
            {"Navn": "Kari Nordmann", "Telefon": "99887766", "Melding": "Størrelse 58"},
        )
    ]


def test_order_submit_honeypot_drops_silently(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post(
        "/hatter/solhatt/bestill",
        data={"navn": "Bot", "telefon": "123", "melding": "", "website": "spam.example"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Takk" in response.get_data(as_text=True)
    assert sent_mail == []


def test_order_submit_requires_name_and_phone(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post(
        "/hatter/solhatt/bestill",
        data={"navn": "", "telefon": "", "melding": "hei"},
    )
    assert response.status_code == 400
    assert "Navn og telefon" in response.get_data(as_text=True)
    assert sent_mail == []


def test_order_submit_mail_failure_shows_error(client: FlaskClient) -> None:
    def broken_mail(subject: str, fields: dict[str, str]) -> None:
        raise ConnectionError("smtp down")

    client.application.config["SEND_MAIL"] = broken_mail
    response = client.post(
        "/hatter/solhatt/bestill",
        data={"navn": "Kari", "telefon": "99887766", "melding": ""},
    )
    assert response.status_code == 500
    assert "beklager" in response.get_data(as_text=True).lower()
