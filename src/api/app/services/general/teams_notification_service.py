"""Optional Teams Incoming Webhook (nice-to-have) after UC-08 booking."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_appointment_notification(appointment: dict[str, Any]) -> bool:
    """POST a simple MessageCard to Teams. Returns True if HTTP 2xx."""
    settings = get_settings()
    url = (settings.teams_webhook_url or "").strip()
    if not url:
        return False

    sev = str(appointment.get("severity", "")).upper()
    title = "MedAssist — New appointment booked"
    facts = [
        {"name": "Code", "value": str(appointment.get("appointment_code", ""))},
        {"name": "When", "value": str(appointment.get("scheduled_at", ""))},
        {"name": "Department", "value": str(appointment.get("department_name", ""))},
        {"name": "Doctor", "value": str(appointment.get("doctor_name", ""))},
        {"name": "Patient", "value": str(appointment.get("patient_name", ""))},
        {"name": "Phone", "value": str(appointment.get("patient_phone", ""))},
        {"name": "Severity", "value": sev},
    ]
    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": "D0021B" if sev == "URGENT" else "0078D4",
        "summary": title,
        "sections": [
            {
                "activityTitle": title,
                "activitySubtitle": "Workshop demo notification",
                "facts": facts,
                "markdown": True,
            }
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as exc:
        logger.warning("Teams webhook HTTP error: %s", exc)
    except urllib.error.URLError as exc:
        logger.warning("Teams webhook URL error: %s", exc)
    except Exception:
        logger.exception("Teams webhook failed")
    return False
