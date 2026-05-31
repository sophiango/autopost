import base64
import os
from datetime import datetime
from openai import OpenAI, BadRequestError

client = OpenAI()

SAFE_FALLBACK_SUFFIX = (
    " Peaceful, uplifting scene. No text, no words, no letters in the image."
)


_DEFAULT_SAVE_DIR = "/tmp/images" if os.environ.get("VERCEL") else "images"


def generate_image(prompt: str, size: str = "1024x1024", save_dir: str = _DEFAULT_SAVE_DIR) -> str:
    os.makedirs(save_dir, exist_ok=True)

    def attempt(p: str) -> str:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=p,
            size=size,
            quality="low",
            n=1,
        )
        image_bytes = base64.b64decode(response.data[0].b64_json)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(save_dir, f"image_{timestamp}.png")

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        return file_path

    try:
        return attempt(prompt)
    except BadRequestError as e:
        print(f"Image content policy rejection — retrying with safer prompt. Error: {e}")
        return attempt(prompt + SAFE_FALLBACK_SUFFIX)
