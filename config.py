import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    openai_api_key: str
    meta_access_token: str
    facebook_page_id: str
    content_niche: str
    content_language: str
    image_size: str
    post_schedule_hours: int


def load_config() -> Config:
    missing = []

    required = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "META_ACCESS_TOKEN": os.getenv("META_ACCESS_TOKEN"),
        "FACEBOOK_PAGE_ID": os.getenv("FACEBOOK_PAGE_ID"),
    }

    for key, val in required.items():
        if not val:
            missing.append(key)

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in all values."
        )

    return Config(
        openai_api_key=required["OPENAI_API_KEY"],
        meta_access_token=required["META_ACCESS_TOKEN"],
        facebook_page_id=required["FACEBOOK_PAGE_ID"],
        content_niche=os.getenv("CONTENT_NICHE", "quotes and motivation sayings in vietnamese"),
        content_language=os.getenv("CONTENT_LANGUAGE", "Vietnamese"),
        image_size=os.getenv("IMAGE_SIZE", "1024x1024"),
        post_schedule_hours=int(os.getenv("POST_SCHEDULE_HOURS", "24")),
    )
