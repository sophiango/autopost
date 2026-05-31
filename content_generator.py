import json
import random
from openai import OpenAI, RateLimitError
import time

client = OpenAI()

NICHES = [
    "buông bỏ và tha thứ cho bản thân",          # letting go and self-forgiveness
    "sống chậm và trân trọng khoảnh khắc hiện tại",  # slow living and present moment
    "chữa lành sau kiệt sức",                    # healing from burnout
    "những câu nói truyền cảm hứng buổi sáng",   # morning motivational quotes
    "bình yên trong sự đơn giản",                 # peace in simplicity
    "lòng biết ơn và những điều nhỏ bé",          # gratitude for small things
    "kiên nhẫn với hành trình của chính mình",    # patience with your own journey
    "tự yêu thương bản thân",                     # self-love
    "vượt qua nỗi sợ hãi và nghi ngờ bản thân",  # overcoming fear and self-doubt
    "ý nghĩa của sự cô đơn lành mạnh",            # meaning of healthy solitude
    "những bài học từ thiên nhiên",               # lessons from nature
    "sự dũng cảm trong cuộc sống hàng ngày",      # courage in everyday life
    "tìm lại chính mình sau những thay đổi lớn",  # rediscovering yourself after big changes
    "giá trị của sự im lặng và nghỉ ngơi",        # value of silence and rest
    "những câu chuyện nhỏ về hy vọng",            # small stories of hope
]


def pick_niche() -> str:
    return random.choice(NICHES)


def generate_content(niche: str, avoid_topics: list[str] = []) -> dict:
    avoid_str = ", ".join(avoid_topics) if avoid_topics else "none"

    system_prompt = (
        "You are a Vietnamese mindfulness writer and visual storyteller. "
        "You create calm, reflective Facebook posts for a page called 'Sống Chậm Lại'. "
        "The page focuses on slow living, inner peace, healing from burnout, "
        "simple daily moments, and emotional rest. "
        "Your writing is gentle, poetic, human, and comforting — never promotional. "
        "Avoid toxic positivity, politics, religion, and sales language. "
        "All written content must be in natural Vietnamese. "
        "Image prompts must be written in English, cinematic, calm, minimal, and cozy. "
        "Always respond in valid JSON only."
    )

    user_prompt = (
        f"Create one Facebook post for the Vietnamese page 'Sống Chậm Lại'.\n"
        f"Main theme: {niche}.\n"
        f"Avoid these topics: {avoid_str}.\n\n"

        "TEXT CONTENT RULES:\n"
        "- Tone: calm, gentle, reflective\n"
        "- Style: short paragraphs, easy to read\n"
        "- Length: 80–150 words\n"
        "- Max 1–2 emojis if appropriate\n\n"

        "IMAGE PROMPT RULES:\n"
        "- Written in ENGLISH\n"
        "- Calm, cinematic, cozy, minimal\n"
        "- Vietnamese atmosphere preferred\n"
        "- No text, no logos, no faces\n"
        "- Natural light, soft colors\n\n"

        "Return JSON with keys:\n"
        "- topic (Vietnamese)\n"
        "- title (Vietnamese, max 10 words)\n"
        "- description (Vietnamese)\n"
        "- call_to_action (Vietnamese, gentle)\n"
        "- hashtags (list of 8–15 Vietnamese hashtags)\n"
        "- image_prompt (English, for AI image generation)\n"
    )

    def call_api(strict: bool = False) -> dict:
        prompt = user_prompt if not strict else user_prompt + "\nReturn ONLY raw JSON, no markdown fences."
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    try:
        return call_api()
    except RateLimitError:
        print("Rate limit hit — waiting 60s before retry...")
        time.sleep(60)
        return call_api()
    except json.JSONDecodeError:
        print("JSON parse failed — retrying with stricter prompt...")
        return call_api(strict=True)


def generate_post(niche: str, avoid_topics: list[str] = []) -> dict:
    from image_generator import generate_image

    content = generate_content(niche, avoid_topics)
    image_path = generate_image(content["image_prompt"])

    return {
        "topic": content["topic"],
        "title": content["title"],
        "description": content["description"],
        "call_to_action": content.get("call_to_action", ""),
        "hashtags": content["hashtags"],
        "image_prompt": content["image_prompt"],
        "image_path": image_path,
    }
