from unittest import mock

import pytest

from fraoverstebenk.mail import send_form_email, settings_from_env

ENV = {
    "SMTP_HOST": "smtp.example.com",
    "SMTP_USERNAME": "bruker",
    "SMTP_PASSWORD": "hemmelig",
    "MAIL_FROM": "nettside@example.com",
    "MAIL_TO": "carl@example.com",
}


def test_settings_from_env_with_default_port() -> None:
    settings = settings_from_env(ENV)
    assert settings.host == "smtp.example.com"
    assert settings.port == 587
    assert settings.to_addr == "carl@example.com"


def test_settings_from_env_missing_variable_raises() -> None:
    with pytest.raises(KeyError):
        settings_from_env({})


def test_send_form_email_uses_starttls_and_sends() -> None:
    settings = settings_from_env(ENV)
    with mock.patch("fraoverstebenk.mail.smtplib.SMTP") as smtp_class:
        smtp = smtp_class.return_value.__enter__.return_value
        send_form_email(settings, "Bestilling: Solhatt", {"Navn": "Kari", "Telefon": "99887766"})
    smtp_class.assert_called_once_with("smtp.example.com", 587)
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with("bruker", "hemmelig")
    message = smtp.send_message.call_args.args[0]
    assert message["Subject"] == "Bestilling: Solhatt"
    assert message["From"] == "nettside@example.com"
    assert message["To"] == "carl@example.com"
    assert "Navn: Kari" in message.get_content()
    assert "Telefon: 99887766" in message.get_content()
