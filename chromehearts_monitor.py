import json
import os
import time
import requests

URL = "https://waitwhile.com/locations/chromehearts/time?registration=booking"
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK", "https://hooks.slack.com/triggers/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")
POLL_INTERVAL = 10  # seconds

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_available_slots():
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.text

    marker = '__NEXT_DATA__" type="application/json">'
    start = html.find(marker)
    if start == -1:
        raise ValueError("__NEXT_DATA__ marker not found in page")
    start += len(marker)

    end = html.find("</script>", start)
    if end == -1:
        raise ValueError("Closing </script> not found after __NEXT_DATA__")

    data = json.loads(html[start:end])
    slot_ids = (
        data.get("props", {})
            .get("ssrLocationData", {})
            .get("availableBookingResourceIds", [])
    )
    return slot_ids


def send_slack_alert(slot_ids):
    if not SLACK_WEBHOOK:
        print("[WARN] SLACK_WEBHOOK not set — skipping notification")
        return

    booking_url = "https://waitwhile.com/locations/chromehearts/time?registration=booking"
    ids_text = ", ".join(str(s) for s in slot_ids)
    payload = {
        "text": (
            f"🚨 *Chrome Hearts slot open!*\n"
            + f"<{booking_url}|Book now>\n"
            + f"Slot IDs: `{ids_text}`"
        )
    }
    r = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
    r.raise_for_status()
    print(f"[INFO] Slack alert sent (slots: {ids_text})")


def main():
    had_slots = False
    print("[INFO] Chrome Hearts monitor started. Polling every 10s\u2026")

    while True:
        try:
            slot_ids = fetch_available_slots()
            has_slots = bool(slot_ids)

            if has_slots and not had_slots:
                print(f"[ALERT] Slots opened: {slot_ids}")
                send_slack_alert(slot_ids)
            elif not has_slots and had_slots:
                print("[INFO] Slots are gone again — watching for next opening")
            else:
                status = f"slots available: {slot_ids}" if has_slots else "no slots"
                print(f"[poll] {status}")

            had_slots = has_slots

        except Exception as exc:
            print(f"[ERROR] {exc}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
