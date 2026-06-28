# Chrome Hearts Slot Monitor

Polls the Chrome Hearts Waitwhile booking page every 10 seconds and fires a Slack alert the moment a slot opens.

## How it works

1. Fetches `waitwhile.com/locations/chromehearts/time?registration=booking` (plain HTTP — no headless browser)
2. Parses the `__NEXT_DATA__` JSON blob embedded in the HTML
3. Checks `props.ssrLocationData.availableBookingResourceIds`
4. Sends a Slack message **only once** when the list goes from empty → non-empty; resets when slots disappear so the next opening triggers again

---

## Local setup

**Prerequisites:** Python 3.8+

```bash
pip install -r requirements.txt
export SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
python chromehearts_monitor.py
```

Console output on every poll; Slack fires only on state change.

---

## Deploy to Railway

Railway will keep the script running 24/7 for free (within the hobby tier limits).

1. **Create a new project** at [railway.app](https://railway.app) → *New Project* → *Deploy from GitHub repo*

2. **Set the environment variable** in Railway:
   - Go to your service → *Variables* tab
   - Add `SLACK_WEBHOOK` = your webhook URL (optional — it's already baked in)

3. **Deploy** — Railway auto-detects Python, installs `requirements.txt`, and starts the worker.

Check the *Logs* tab to confirm polling has started.

---

## Getting a Slack webhook URL

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → *Create New App* → *From scratch*
2. Under *Features*, choose *Incoming Webhooks* → toggle on → *Add New Webhook to Workspace*
3. Pick the channel to post to, authorize, and copy the webhook URL
