from config import load_config
from content_generator import generate_post, pick_niche
from facebook_publisher import post_to_facebook, build_caption
from logger import log_post, get_recent_topics


def run_agent():
    config = load_config()

    print("=== Autopost Agent Starting ===")

    # 1. Avoid repeating recent topics
    recent = get_recent_topics(10)
    if recent:
        print(f"Avoiding recent topics: {recent}")

    # 2. Pick niche, generate content + image
    niche = pick_niche()
    print(f"\n[1/3] Generating content and image... (niche: {niche})")
    post = generate_post(niche, avoid_topics=recent)
    print(f"  Topic:  {post['topic']}")
    print(f"  Title:  {post['title']}")
    print(f"  Image:  {post['image_path']}")

    # 3. Build caption and post to Facebook
    caption = build_caption(post["title"], post["description"], post["hashtags"])
    print("\n[2/3] Posting to Facebook...")
    fb_id = post_to_facebook(post["image_path"], caption, config.facebook_page_id, config.meta_access_token)
    print(f"  Post ID: {fb_id}")

    # 4. Log
    print("\n[3/3] Logging post...")
    log_post(post, post["image_path"], fb_id)

    print("\n=== Done. Post published and logged. ===")


if __name__ == "__main__":
    run_agent()
