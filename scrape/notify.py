from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText


def find_newly_blocked_dates(old_days: dict[str, str], new_days: list[dict]) -> list[dict]:
    """
    Returns entries from `new_days` whose status is "unavailable" but wasn't
    "unavailable" in `old_days` (i.e. newly booked/blocked since the last run).

    `old_days` maps date -> status from the previous run's latest.json.
    `new_days` is the freshly aggregated per-apartment day list.
    """
    return [
        day
        for day in new_days
        if day.get("status") == "unavailable" and old_days.get(day.get("date")) != "unavailable"
    ]


def send_email(subject: str, body: str, to_addr: str) -> None:
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr

    with smtplib.SMTP_SSL(host, port) as server:
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())
