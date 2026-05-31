# CLAUDE.md — Autonomous Facebook Content Agent

## Project overview

An autonomous Python agent that:
1. Randomly picks a niche from a curated Vietnamese slow-living theme list
2. Uses GPT-4o to generate a Vietnamese caption (title, description, call to action, hashtags)
3. Uses gpt-image-1 to generate a matching image (returned as base64, saved locally)
4. Posts the image + caption to a Facebook Page via Meta Graph API
5. Logs every post to `posts_log.json` to avoid repeating topics

The agent runs on a schedule (cron or manual trigger). No human approval required — fully autonomous.

---

## Tech stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| AI text | OpenAI GPT-4o (chat completions) |
| AI image | OpenAI gpt-image-1 (images API, quality: low) |
| Social posting | Meta Graph API v25.0 |
| Scheduling | `schedule` library or cron |
| Config | `.env` file |
| HTTP | `requests` |

---

## Project structure

```
autopost/
├── main.py                 # Entry point — runs the full agent pipeline
├── content_generator.py    # GPT-4o: generates caption + picks random niche
├── image_generator.py      # gpt-image-1: generates image, saves as PNG
├── facebook_publisher.py   # Meta Graph API: posts to Facebook Page
├── scheduler.py            # Runs agent on a 24h schedule
├── test_post.py            # Tests Facebook posting with hardcoded content (no token cost)
├── post_existing.py        # Posts images in images/ not yet published
├── logger.py               # Logs posts to posts_log.json
├── config.py               # Loads and validates all env vars
├── posts_log.json          # Auto-created. Tracks all published posts (gitignored)
├── images/                 # Generated images saved here (gitignored)
├── .env                    # All secrets (gitignored)
├── .env.example
├── requirements.txt
└── .gitignore
```

---

## Environment variables

### `.env.example`
```
# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Meta Graph API
META_ACCESS_TOKEN=your-long-lived-page-access-token
FACEBOOK_PAGE_ID=your-facebook-page-id

# Agent config
CONTENT_LANGUAGE=Vietnamese
IMAGE_SIZE=1024x1024
POST_SCHEDULE_HOURS=24
```

Note: `CONTENT_NICHE` is no longer used. Niches are randomized from the `NICHES` list in `content_generator.py`.

---

## Module specs

### `config.py`
- Load all env vars via `python-dotenv`
- Validate required keys on startup; raise descriptive errors if missing
- Expose a `Config` dataclass with all settings

---

### `content_generator.py`

#### `NICHES` list
A curated list of 15 Vietnamese slow-living/motivational themes. One is picked randomly each run via `pick_niche()`. To add or remove themes, edit this list directly.

```python
NICHES = [
    "buông bỏ và tha thứ cho bản thân",
    "sống chậm và trân trọng khoảnh khắc hiện tại",
    "chữa lành sau kiệt sức",
    # ... 12 more
]
```

#### `pick_niche() -> str`
Returns a random entry from `NICHES`.

#### `generate_content(niche: str, avoid_topics: list[str] = []) -> dict`

Calls GPT-4o to generate a complete social media post for the page **"Sống Chậm Lại"**. Returns:

```python
{
  "topic": "...",           # Short topic label, in Vietnamese
  "title": "...",           # Hook line, max 10 words, in Vietnamese
  "description": "...",     # 80–150 word caption body, in Vietnamese
  "call_to_action": "...",  # Gentle closing line, in Vietnamese
  "hashtags": [...],        # 8–15 Vietnamese hashtags as a list
  "image_prompt": "..."     # Detailed prompt in English for gpt-image-1
}
```

System prompt persona: calm Vietnamese mindfulness writer. Tone is gentle, poetic, human — never promotional. No toxic positivity, politics, religion, or sales language.

If JSON parsing fails, retries once with a stricter prompt.

#### `generate_post(niche: str, avoid_topics: list[str] = []) -> dict`

Combined helper that calls `generate_content()` then `generate_image()` and returns everything together:

```python
{
  "topic": "...",
  "title": "...",
  "description": "...",
  "call_to_action": "...",
  "hashtags": [...],
  "image_prompt": "...",
  "image_path": "images/image_20260530_143022.png"   # local file path
}
```

This is what `main.py` calls — it is the primary entry point for generation.

---

### `image_generator.py`

**Function: `generate_image(prompt: str, size: str = "1024x1024", save_dir: str = "images") -> str`**

- Calls OpenAI Images API with **gpt-image-1**, quality `"low"`
- Response is `b64_json` — decoded with `base64.b64decode()`, no HTTP download needed
- Saves to `images/` with a timestamp filename: `image_20260530_143022.png`
- Returns the local file path

```python
response = client.images.generate(
    model="gpt-image-1",
    prompt=prompt,
    size=size,        # "1024x1024"
    quality="low",    # low | medium | high
    n=1,
)
image_bytes = base64.b64decode(response.data[0].b64_json)
```

On content policy rejection (`BadRequestError`), retries once with a safe suffix appended to the prompt.

---

### `facebook_publisher.py`

Base URL: `https://graph.facebook.com/v25.0`

Posts a photo to a Facebook Page by uploading the local image file directly:

```
POST /{page_id}/photos
  Form data:
    source=<binary image file>
    message=<caption text>
    access_token=<page access token>
```

**Function: `post_to_facebook(image_path: str, caption: str, page_id: str, access_token: str) -> str`**

Returns the post ID string. Raises `RuntimeError` with the full Meta error body on 4xx responses (do not retry automatically — the error body is descriptive).

**Function: `build_caption(title: str, description: str, hashtags) -> str`**

Builds the caption string:
```
{title}\n\n{description}\n\n{hashtags joined by spaces}
```

---

### `logger.py`

**`log_post(content: dict, image_file: str, facebook_post_id: str)`**

Appends to `posts_log.json`:
```json
{
  "timestamp": "2026-05-30T14:30:22",
  "topic": "...",
  "title": "...",
  "image_file": "images/image_20260530_143022.png",
  "facebook_post_id": "...",
  "hashtags": "..."
}
```

**`get_recent_topics(n: int = 10) -> list[str]`**

Returns the last `n` topic strings from the log. Returns `[]` if the file doesn't exist. Passed to `generate_content()` so the agent avoids repeating topics.

---

### `main.py`

Full pipeline (3 steps):

```python
def run_agent():
    config = load_config()
    recent = get_recent_topics(10)

    # 1. Pick niche, generate content + image in one call
    niche = pick_niche()
    post = generate_post(niche, avoid_topics=recent)

    # 2. Post to Facebook
    caption = build_caption(post["title"], post["description"], post["hashtags"])
    fb_id = post_to_facebook(post["image_path"], caption, config.facebook_page_id, config.meta_access_token)

    # 3. Log
    log_post(post, post["image_path"], fb_id)
```

---

### `scheduler.py`

Runs `run_agent()` once immediately on start, then every N hours (from `POST_SCHEDULE_HOURS` in `.env`, default 24).

---

### `test_post.py`

Posts a hardcoded caption + existing image from `images/` to Facebook. Use this to verify token and Page ID are correct without spending any OpenAI tokens.

---

### `post_existing.py`

Scans `images/` for `.png` files not yet in `posts_log.json`. For each unposted image, generates a fresh GPT-4o caption and posts it. Useful for recovering from failed runs where images were generated but posting failed.

---

## How to get your Facebook credentials

**Critical:** You must use a **Page Access Token**, not a User Access Token. They look identical but the User token will return a 403 `publish_actions` error.

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer)
2. Select your app, click **Generate Access Token**, approve the popup
3. Run `GET /me/accounts`
4. In the response JSON, find your Page and copy its own `"access_token"` field
5. Also copy the `"id"` field — that is your `FACEBOOK_PAGE_ID`
6. Paste the token into `.env` as `META_ACCESS_TOKEN`

Token expires in ~60 days. Regenerate via `/me/accounts` when you see a 403 or 190 error.

---

## Error handling

- **OpenAI rate limit:** catch `RateLimitError`, wait 60s, retry once
- **gpt-image-1 content policy rejection:** catch `BadRequestError`, retry with safe suffix appended to prompt
- **Meta API 400/403:** raise `RuntimeError` with full response body, do not retry automatically
- **JSON parse failure from GPT:** retry once with `"Return ONLY raw JSON, no markdown fences"`
- **Missing env vars:** fail fast at startup with a clear list of which vars are missing
- **Image file not found:** raise `FileNotFoundError` with descriptive message before attempting to post

---

## .gitignore
```
.env
images/
posts_log.json
__pycache__/
*.pyc
```

---

## Requirements.txt

```
openai>=1.0.0
requests
python-dotenv
Pillow
schedule
```

---

## What Claude Code must NOT do

- Never post to personal Facebook profiles (API only supports Pages)
- Never store the access token anywhere except `.env`
- Never hardcode any API keys
- Never send more than 1 post per run in `main.py` (scheduler handles frequency)
- Do not include any Instagram code, imports, or references
- Do not switch back to `dall-e-3` unless explicitly asked — gpt-image-1 is the current model
