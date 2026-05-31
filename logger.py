import json
import os
from datetime import datetime

LOG_FILE = "posts_log.json"


def log_post(content: dict, image_file: str, facebook_post_id: str) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "topic": content.get("topic", ""),
        "title": content.get("title", ""),
        "image_file": image_file,
        "facebook_post_id": facebook_post_id,
        "hashtags": content.get("hashtags", ""),
    }

    posts = _read_log()
    posts.append(entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def get_recent_topics(n: int = 10) -> list[str]:
    posts = _read_log()
    return [p["topic"] for p in posts[-n:] if p.get("topic")]


def _read_log() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
