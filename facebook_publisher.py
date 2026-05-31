import requests

BASE_URL = "https://graph.facebook.com/v25.0"


def post_to_facebook(image_path: str, caption: str, page_id: str, access_token: str) -> str:
    if not image_path or not __import__("os").path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    url = f"{BASE_URL}/{page_id}/photos"

    with open(image_path, "rb") as image_file:
        response = requests.post(
            url,
            data={
                "message": caption,
                "access_token": access_token,
            },
            files={"source": image_file},
        )

    if not response.ok:
        raise RuntimeError(
            f"Meta API error {response.status_code}:\n{response.text}"
        )

    data = response.json()
    post_id = data.get("post_id") or data.get("id")
    return post_id


def build_caption(title: str, description: str, hashtags: str) -> str:
    return f"{title}\n\n{description}\n\n{hashtags}"
