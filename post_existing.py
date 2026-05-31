"""
Posts all images in the images/ folder that haven't been logged yet.
Generates a fresh caption for each one using GPT-4o.

Usage:
    python post_existing.py
"""

import os
from config import load_config
from content_generator import generate_content, pick_niche
from facebook_publisher import post_to_facebook, build_caption
from logger import log_post, get_recent_topics


def get_unposted_images(images_dir: str = "images") -> list[str]:
    logged = _get_logged_image_paths()
    all_images = sorted(
        os.path.join(images_dir, f)
        for f in os.listdir(images_dir)
        if f.endswith(".png") or f.endswith(".jpg")
    )
    return [img for img in all_images if img not in logged]


def _get_logged_image_paths() -> set[str]:
    from logger import _read_log
    return {entry.get("image_file", "") for entry in _read_log()}


def main():
    config = load_config()

    unposted = get_unposted_images()
    if not unposted:
        print("No unposted images found.")
        return

    print(f"Found {len(unposted)} unposted image(s): {unposted}\n")

    recent = get_recent_topics(10)

    for i, image_path in enumerate(unposted, 1):
        print(f"[{i}/{len(unposted)}] Processing {image_path}")

        print("  Generating caption with GPT-4o...")
        niche = pick_niche()
        content = generate_content(niche, avoid_topics=recent)
        print(f"  Topic: {content['topic']}")
        print(f"  Title: {content['title']}")

        caption = build_caption(content["title"], content["description"], content["hashtags"])

        print("  Posting to Facebook...")
        fb_id = post_to_facebook(image_path, caption, config.facebook_page_id, config.meta_access_token)
        print(f"  Posted! ID: {fb_id}")

        log_post(content, image_path, fb_id)
        recent.append(content["topic"])
        print()

    print("All done.")


if __name__ == "__main__":
    main()
