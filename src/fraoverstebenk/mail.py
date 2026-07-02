from __future__ import annotations

import os
import smtplib
from collections.abc import Mapping
from dataclasses import dataclass
from email.message import EmailMessage


@dataclass(frozen=True)
class MailSettings:
    host: str
    port: int
    username: str
    password: str
    from_addr: str
    to_addr: str


def settings_from_env(env: Mapping[str, str] | None = None) -> MailSettings:
    if env is None:
        env = os.environ
    return MailSettings(
        host=env["SMTP_HOST"],
        port=int(env.get("SMTP_PORT", "587")),
        username=env["SMTP_USERNAME"],
        password=env["SMTP_PASSWORD"],
        from_addr=env["MAIL_FROM"],
        to_addr=env["MAIL_TO"],
    )


def send_form_email(settings: MailSettings, subject: str, fields: dict[str, str]) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.from_addr
    message["To"] = settings.to_addr
    message.set_content("\n".join(f"{label}: {value}" for label, value in fields.items()))
    with smtplib.SMTP(settings.host, settings.port) as smtp:
        smtp.starttls()
        smtp.login(settings.username, settings.password)
        smtp.send_message(message)
