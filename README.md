# Autonomous Facebook Content Agent

Generates and posts Vietnamese motivational content to a Facebook Page on a schedule. No human approval required.

## How it works

1. Randomly picks a niche from a curated list of Vietnamese slow-living themes
2. Uses **GPT-4o** to generate a Vietnamese caption (title, description, hashtags)
3. Uses **gpt-image-1** (quality: low) to generate a matching image
4. Posts the image + caption to a Facebook Page via Meta Graph API
5. Logs every post to `posts_log.json` to avoid repeating topics

## Project structure

```
autopost/
├── main.py               # Full pipeline — run once per post
├── scheduler.py          # Runs main.py every 24h automatically
├── test_post.py          # Test Facebook posting with hardcoded content (no API cost)
├── post_existing.py      # Post images already in images/ that haven't been published yet
├── content_generator.py  # GPT-4o: generates caption + picks random niche
├── image_generator.py    # gpt-image-1: generates image, saves as PNG
├── facebook_publisher.py # Meta Graph API: uploads image + caption to Page
├── logger.py             # Reads/writes posts_log.json
├── config.py             # Loads and validates .env
├── images/               # Generated images saved here (gitignored)
├── posts_log.json        # Published post history (gitignored)
├── .env                  # Your secrets (gitignored)
├── .env.example          # Template
└── requirements.txt
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

```
OPENAI_API_KEY=sk-...
META_ACCESS_TOKEN=EAABsb...
FACEBOOK_PAGE_ID=123456789
```

### 3. Get your Facebook Page Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer)
2. Select your app, click **Generate Access Token**, approve the popup
3. Run `GET /me/accounts`
4. In the response, copy the `access_token` from your **Page entry** (not the top-level Explorer token)
5. Paste it as `META_ACCESS_TOKEN` in `.env`

> The token from `/me/accounts` is long-lived but expires after ~60 days. Regenerate it when you see a 403 error.

## Usage

### Run once

```bash
python main.py
```

### Run on a 24-hour schedule

```bash
python scheduler.py
```

Runs once immediately, then every 24 hours.

### Test Facebook posting without spending tokens

```bash
python test_post.py
```

Uses a hardcoded caption and an existing image from `images/`. Use this to verify your token and Page ID are correct before running the full pipeline.

### Post images that were already generated but not yet published

```bash
python post_existing.py
```

Finds any `.png` files in `images/` not in `posts_log.json`, generates a fresh caption for each, and posts them.

## Models used

| Task | Model |
|---|---|
| Caption generation | GPT-4o |
| Image generation | gpt-image-1 (quality: low) |

### Why gpt-image-1?
- Returns images as base64 (`b64_json`) — no expiring download URLs
- Supports `quality` parameter: `low`, `medium`, `high`
- `low` quality is used by default to reduce cost per post

## Content niches

Each post picks randomly from 15 Vietnamese slow-living themes defined in `content_generator.py`:

- Buông bỏ và tha thứ cho bản thân
- Sống chậm và trân trọng khoảnh khắc hiện tại
- Chữa lành sau kiệt sức
- Những câu nói truyền cảm hứng buổi sáng
- Bình yên trong sự đơn giản
- Lòng biết ơn và những điều nhỏ bé
- *(and 9 more — see `NICHES` list in `content_generator.py`)*

To add or remove niches, edit the `NICHES` list in `content_generator.py`.

## Cost per post (approximate)

| Step | Cost |
|---|---|
| GPT-4o caption | ~$0.01 |
| gpt-image-1 low quality | ~$0.02 |
| **Total** | **~$0.03** |

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Missing required environment variables` | `.env` not filled in | Fill in all three keys |
| `Meta API error 190` | Token expired | Regenerate via `/me/accounts` in Graph API Explorer |
| `Meta API error 403 publish_actions` | Using User token, not Page token | Copy the token from the Page entry in `/me/accounts`, not the Explorer header |
| `AuthenticationError` | Wrong OpenAI key | Check `OPENAI_API_KEY` in `.env` |
| `model_not_found` for gpt-image-1 | Model not enabled on your account | Enable image generation at platform.openai.com/settings or switch to `dall-e-3` |
