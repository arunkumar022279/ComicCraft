import base64
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

API_KEY = os.getenv("GEMINI_API_KEY")

TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.8-flash"
)

IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
)

if not API_KEY:
    raise RuntimeError(
        f"GEMINI_API_KEY is missing.\n"
        f"Please check your .env file:\n{ENV_FILE}"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR = BASE_DIR / "static" / "generated"
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# HELPER: DETECT TEMPORARY ERRORS
# ============================================================

def is_temporary_error(exc):

    status_code = getattr(
        exc,
        "status_code",
        None
    )

    if status_code in {
        429,
        500,
        502,
        503,
        504
    }:
        return True

    message = str(exc).upper()

    temporary_words = [
        "429",
        "500",
        "502",
        "503",
        "504",
        "UNAVAILABLE",
        "RESOURCE_EXHAUSTED",
        "DEADLINE_EXCEEDED",
        "RATE LIMIT",
        "HIGH DEMAND",
    ]

    return any(
        word in message
        for word in temporary_words
    )


# ============================================================
# HELPER: EXTRACT JSON
# ============================================================

def extract_json(text):

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # Remove markdown JSON fences if Gemini adds them.
    if text.startswith("```"):

        text = (
            text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:

        raise RuntimeError(
            "Gemini did not return valid JSON."
        )

    json_text = text[
        start:end + 1
    ]

    try:

        return json.loads(
            json_text
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc


# ============================================================
# GENERATE COMIC STORY
# ============================================================

def generate_comic_outline(data):

    prompt = f"""
You are the creative director of ComicCraft,
a premium AI comic studio.

Create a complete {data.panels}-panel comic.

USER STORY IDEA:
{data.story_prompt}

MAIN CHARACTER:
{data.character_name}

SETTING:
{data.setting}

TONE:
{data.tone}

ART STYLE:
{data.art_style}

IMPORTANT REQUIREMENTS:

1. Create a coherent story from panel 1 to the final panel.
2. Keep the main character visually consistent.
3. Make the story family-friendly.
4. Make every panel visually interesting.
5. Give every panel a strong visual moment.
6. Keep dialogue short enough for a comic speech bubble.
7. Do NOT put written dialogue inside image prompts.
8. Do NOT ask the image model to render text.
9. Make each panel visually different.
10. End with a satisfying final panel.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
    "title": "comic title",
    "tagline": "short exciting tagline",
    "panels": [
        {{
            "number": 1,
            "title": "panel title",
            "scene": "visual scene description",
            "narration": "short narration",
            "dialogue": "short spoken dialogue",
            "caption": "short comic caption",
            "image_prompt": "detailed visual prompt"
        }}
    ]
}}
"""


    print(
        f"\nComicCraft: generating story with "
        f"{TEXT_MODEL}"
    )


    # ========================================================
    # NEW INTERACTIONS API
    # ========================================================

    try:

        interaction = client.interactions.create(

            model=TEXT_MODEL,

            input=prompt,

            response_format={
                "type": "text",
                "mime_type": "application/json"
            }
        )

    except Exception as exc:

        print(
            f"ComicCraft Gemini error: "
            f"{type(exc).__name__}: {exc}"
        )

        if is_temporary_error(exc):

            raise RuntimeError(
                "Gemini is temporarily unavailable "
                "or the API rate limit has been reached. "
                "Please try again later."
            ) from exc

        raise RuntimeError(
            f"Gemini request failed: {exc}"
        ) from exc


    # ========================================================
    # GET TEXT OUTPUT
    # ========================================================

    response_text = getattr(
        interaction,
        "output_text",
        None
    )


    if not response_text:

        raise RuntimeError(
            "Gemini returned no story text."
        )


    # ========================================================
    # CONVERT JSON
    # ========================================================

    comic = extract_json(
        response_text
    )


    # ========================================================
    # VALIDATE
    # ========================================================

    if "title" not in comic:

        comic["title"] = (
            "My Comic Adventure"
        )


    if "tagline" not in comic:

        comic["tagline"] = (
            "An amazing AI-generated adventure!"
        )


    if "panels" not in comic:

        raise RuntimeError(
            "Gemini response does not contain panels."
        )


    if not isinstance(
        comic["panels"],
        list
    ):

        raise RuntimeError(
            "Gemini panels are not a list."
        )


    if len(comic["panels"]) == 0:

        raise RuntimeError(
            "Gemini returned zero panels."
        )


    print(
        f"ComicCraft: generated "
        f"{len(comic['panels'])} panels"
    )


    return comic


# ============================================================
# GENERATE PANEL IMAGE
# ============================================================

def generate_panel_image(
    image_prompt,
    panel_number,
    comic_title
):

    visual_prompt = f"""
Create a polished comic-book illustration
for panel {panel_number} of "{comic_title}".

SCENE:
{image_prompt}

VISUAL DIRECTION:

- expressive cute cartoon characters
- bold clean ink outlines
- rich cel-shaded colors
- cinematic lighting
- dynamic composition
- playful professional children's graphic-novel aesthetic
- consistent character design
- consistent character appearance
- expressive facial expressions
- detailed environment
- strong storytelling composition
- landscape comic panel composition
- high-quality digital illustration

IMPORTANT:

- no speech bubbles
- no captions
- no readable text
- no letters
- no logos
- no watermarks
- do not render dialogue
- do not render written words
"""


    print(
        f"ComicCraft: generating image "
        f"for panel {panel_number}"
    )


    # ========================================================
    # NEW INTERACTIONS IMAGE API
    # ========================================================

    try:

        interaction = client.interactions.create(

            model=IMAGE_MODEL,

            input=visual_prompt,

            response_format={
                "type": "image",
                "aspect_ratio": "16:9",
                "image_size": "1K"
            }
        )

    except Exception as exc:

        print(
            f"ComicCraft image error: "
            f"{type(exc).__name__}: {exc}"
        )

        if is_temporary_error(exc):

            raise RuntimeError(
                "Gemini image generation is "
                "temporarily unavailable or "
                "the image API rate limit was reached."
            ) from exc

        raise RuntimeError(
            f"Gemini image generation failed: {exc}"
        ) from exc


    # ========================================================
    # GET IMAGE
    # ========================================================

    image_data = None


    # Normal Interactions API output.

    output_image = getattr(
        interaction,
        "output_image",
        None
    )

    if output_image:

        image_data = getattr(
            output_image,
            "data",
            None
        )


    # ========================================================
    # FALLBACK: SEARCH STEPS
    # ========================================================

    if not image_data:

        for step in (
            getattr(
                interaction,
                "steps",
                []
            )
            or []
        ):

            if getattr(
                step,
                "type",
                ""
            ) != "model_output":

                continue


            for block in (
                getattr(
                    step,
                    "content",
                    []
                )
                or []
            ):

                if getattr(
                    block,
                    "type",
                    ""
                ) == "image":

                    image_data = getattr(
                        block,
                        "data",
                        None
                    )

                    if image_data:
                        break


            if image_data:
                break


    # ========================================================
    # CHECK IMAGE
    # ========================================================

    if not image_data:

        raise RuntimeError(
            "Gemini image generation returned "
            "no image data."
        )


    # ========================================================
    # SAVE IMAGE
    # ========================================================

    safe_title = "".join(
        character
        if character.isalnum()
        else "_"
        for character in comic_title
    )

    filename = (
        f"{safe_title}_"
        f"panel_{panel_number}_"
        f"{int(time.time() * 1000)}.png"
    )

    file_path = (
        OUTPUT_DIR / filename
    )


    try:

        file_path.write_bytes(
            base64.b64decode(
                image_data
            )
        )

    except Exception as exc:

        raise RuntimeError(
            "Could not save the generated image."
        ) from exc


    print(
        f"ComicCraft: saved image "
        f"{file_path}"
    )


    # Return browser URL.

    return (
        "/static/generated/"
        + filename
    )