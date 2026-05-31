"""
Hardcoded test — skips GPT-4o and image generation entirely.
Run this to confirm Facebook posting works before spending tokens.

Usage:
    python test_post.py
"""

from config import load_config
from facebook_publisher import post_to_facebook

# Reuse an already-generated image
TEST_IMAGE = "images/image_20260530_183418.png"

TEST_CAPTION = (
    "🌿 Hôm nay, hãy nhẹ nhàng với chính mình.\n\n"
    "Có những ngày không cần phải làm gì nhiều. "
    "Chỉ cần thở, nhìn ra cửa sổ, và nhắc nhở bản thân rằng — "
    "được tồn tại đã là đủ rồi.\n\n"
    "#SongChamLai #BinhYen #AnNhien #TestPost"
)


def main():
    config = load_config()

    print("=== Facebook Post Test ===")
    print(f"Image:   {TEST_IMAGE}")
    print(f"Page ID: {config.facebook_page_id}")
    print(f"Token:   {config.meta_access_token[:20]}...")
    print()

    fb_id = post_to_facebook(
        TEST_IMAGE,
        TEST_CAPTION,
        config.facebook_page_id,
        config.meta_access_token,
    )
    print(f"Success! Post ID: {fb_id}")


if __name__ == "__main__":
    main()
