# facebook_api.py — Fetches posts from a Facebook Page via the Graph API
# Credentials are stored in config.json (never hard-coded).
# Runs in a background thread so the UI never blocks.

import json
import os
import threading
import urllib.request
import urllib.parse
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# ── Config helpers ────────────────────────────────────────────────────────────

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def get_fb_credentials():
    cfg = load_config()
    return cfg.get("fb_page_id", ""), cfg.get("fb_access_token", "")


def set_fb_credentials(page_id: str, access_token: str):
    cfg = load_config()
    cfg["fb_page_id"] = page_id
    cfg["fb_access_token"] = access_token
    save_config(cfg)


# ── Fetch posts ───────────────────────────────────────────────────────────────

GRAPH_URL = "https://graph.facebook.com/v19.0"


def fetch_posts(limit: int = 10) -> list:
    """
    Fetch recent posts from the configured Facebook Page.
    Returns a list of dicts ready for database.upsert_notices().
    Raises an exception on network / auth error.
    """
    page_id, token = get_fb_credentials()
    if not page_id or not token:
        raise ValueError("Facebook credentials not configured. "
                         "Go to Admin → Facebook Settings to set them up.")

    params = urllib.parse.urlencode({
        "fields": "id,message,story,created_time",
        "limit": limit,
        "access_token": token,
    })
    url = f"{GRAPH_URL}/{page_id}/posts?{params}"

    req = urllib.request.Request(url, headers={"User-Agent": "ASA-SignIn/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())

    posts = []
    for item in data.get("data", []):
        body = item.get("message") or item.get("story") or ""
        if not body:
            continue
        # Facebook timestamps: "2025-03-01T10:30:00+0000"
        raw_time = item.get("created_time", "")
        try:
            dt = datetime.strptime(raw_time[:19], "%Y-%m-%dT%H:%M:%S")
            posted_at = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            posted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # First line as title (truncated)
        title = body.split("\n")[0][:80]
        posts.append({
            "title": title,
            "body": body,
            "post_id": item["id"],
            "posted_at": posted_at,
        })
    return posts


# ── Background refresh ────────────────────────────────────────────────────────

def refresh_notices_async(on_success=None, on_error=None):
    """
    Fetch and save posts in a daemon thread.
    on_success(posts) and on_error(exc) are called on completion
    — schedule them back onto the Tk main thread with .after() if updating UI.
    """
    import database

    def _run():
        try:
            posts = fetch_posts()
            database.upsert_notices(posts)
            if on_success:
                on_success(posts)
        except Exception as exc:
            if on_error:
                on_error(exc)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
