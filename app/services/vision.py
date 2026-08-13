"""
Face vision service.

Does three things:
  1. Cleans the uploaded photo: shrinks it to ~1024px and strips EXIF
     (which removes GPS coordinates - a real privacy risk).
  2. Sends the cleaned photo to GPT-4o for GROOMING analysis only.
  3. Returns a plain dict the app stores and reads later.

Safety rules baked into the prompt (from the product spec):
  - NO attractiveness scores, beauty rankings, or comparisons.
  - Observations are for grooming personalization only.
  - Cautious, non-medical language.

If no API key is set, or the call fails, we return a safe fallback so
onboarding never breaks. The photo is still saved either way.
"""

import base64
import io
import json
import os

from PIL import Image

from app.config import settings


UPLOAD_DIR = "app/static/uploads"


def save_clean_photo(raw_bytes: bytes, user_id: int) -> str:
    """
    Resize to max 1024px on the long edge, drop EXIF, save as JPEG.
    Returns the on-disk path.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    img = Image.open(io.BytesIO(raw_bytes))

    # Convert to RGB (handles PNG/HEIC-ish inputs) and drop all metadata by
    # copying pixel data into a fresh image with no EXIF.
    img = img.convert("RGB")
    img.thumbnail((1024, 1024))
    clean = Image.new("RGB", img.size)
    clean.paste(img)

    path = f"{UPLOAD_DIR}/user_{user_id}_face.jpg"
    clean.save(path, "JPEG", quality=85)
    return path


def _fallback() -> dict:
    """Safe result used when the AI isn't available."""
    return {
        "available": False,
        "face_shape": "Not analyzed",
        "hair": "Not analyzed",
        "skin": "Not analyzed",
        "note": "Add your OpenAI key to enable AI grooming analysis.",
    }


def analyze_face(photo_path: str) -> dict:
    """
    Call GPT-4o vision on the saved photo. Returns a dict with grooming
    observations. Never raises - returns a fallback on any failure.
    """
    if not settings.OPENAI_API_KEY:
        return _fallback()

    try:
        from openai import OpenAI

        with open(photo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # The prompt strictly forbids ratings and asks for JSON only.
        system = (
            "You are a grooming assistant. Look at the face photo and describe "
            "ONLY observable grooming characteristics to help personalize a "
            "haircut and skincare routine. "
            "STRICT RULES: Do NOT give attractiveness scores, beauty ratings, "
            "rankings, or comparisons. Do NOT use insulting words. Do NOT make "
            "medical claims. Use cautious, neutral language. "
            "Respond with ONLY a JSON object, no markdown, with keys: "
            "face_shape (e.g. oval/round/square/heart/oblong), "
            "hair (short phrase on length/texture), "
            "skin (short neutral phrase on apparent skin characteristics)."
        )

        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=300,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this photo for grooming personalization."},
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                },
            ],
        )

        text = resp.choices[0].message.content.strip()
        # Strip accidental code fences if the model added them.
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        data["available"] = True
        return data

    except Exception as e:
        # Log to console for debugging, but never break onboarding.
        print(f"[vision] analysis failed: {e}")
        out = _fallback()
        out["note"] = "AI analysis is temporarily unavailable. Your photo was saved."
        return out
