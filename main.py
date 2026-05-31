from config import load_config
from content_generator import generate_post, pick_niche
from facebook_publisher import post_to_facebook, build_caption


def run_agent():
    config = load_config()

    print("=== Autopost Agent Starting ===")

    niche = pick_niche()
    print(f"\n[1/2] Generating content and image... (niche: {niche})")
    post = generate_post(niche)
    print(f"  Topic: {post['topic']}")
    print(f"  Title: {post['title']}")
    print(f"  Image: {post['image_path']}")

    caption = build_caption(post["title"], post["description"], post["hashtags"])
    print("\n[2/2] Posting to Facebook...")
    fb_id = post_to_facebook(post["image_path"], caption, config.facebook_page_id, config.meta_access_token)
    print(f"  Post ID: {fb_id}")

    print("\n=== Done. ===")


if __name__ == "__main__":
    run_agent()
