from flask.testing import FlaskClient

SentMail = list[tuple[str, dict[str, str]]]


def test_contact_page(client: FlaskClient) -> None:
    response = client.get("/kontakt")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Kontakt" in body
    assert 'name="navn"' in body
    assert 'name="website"' in body


def test_contact_submit_sends_mail(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post(
        "/kontakt",
        data={"navn": "Ola", "telefon": "12345678", "melding": "Hei!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Takk" in response.get_data(as_text=True)
    assert sent_mail == [
        ("Kontaktskjema", {"Navn": "Ola", "Telefon": "12345678", "Melding": "Hei!"})
    ]


def test_contact_submit_honeypot(client: FlaskClient, sent_mail: SentMail) -> None:
    client.post(
        "/kontakt",
        data={"navn": "Bot", "telefon": "1", "melding": "", "website": "x"},
    )
    assert sent_mail == []


def test_contact_submit_requires_name_and_phone(client: FlaskClient, sent_mail: SentMail) -> None:
    response = client.post("/kontakt", data={"navn": "", "telefon": ""})
    assert response.status_code == 400
    assert sent_mail == []


def test_posts_page_renders_all_posts(client: FlaskClient) -> None:
    response = client.get("/godt-a-vite/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Godt å vite" in body
    assert "Stell av hatten" in body
    assert "Børst hatten forsiktig." in body
