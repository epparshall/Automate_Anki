# media_helper.py
import os
import tempfile
from typing import Optional

import requests
import edge_tts  # New import

class MediaHelper:
    @staticmethod
    def generate_tts_audio(text: str, lang: str, output_path: Optional[str] = None) -> str:
        if output_path is None:
            safe_text = "".join(c for c in text if c.isalnum())[:30]
            output_path = os.path.join(tempfile.gettempdir(), f"{lang}_{safe_text}.mp3")

        # Map language codes to strong British voices when needed
        if lang.lower() in ["en-gb", "en-uk"]:
            voice = "en-GB-SoniaNeural"
        elif lang.lower() == "es":
            voice = "es-ES-ElviraNeural"
        elif lang.lower() == "de":
            voice = "de-DE-KatjaNeural"
        elif lang.lower() == "ru":
            voice = "ru-RU-SvetlanaNeural"
        else:
            # Fallback to French or a default
            voice = "fr-FR-DeniseNeural" if lang == "fr" else "en-US-AriaNeural"

        communicate = edge_tts.Communicate(text, voice)
        # Save synchronously (edge-tts supports async, but this is simple)
        import asyncio
        asyncio.run(communicate.save(output_path))

        return output_path

    @staticmethod
    def get_image(query: str, pixabay_api_key: str) -> Optional[str]:
        if not pixabay_api_key or not query.strip():
            return None

        url = "https://pixabay.com/api/"
        params = {
            "key": pixabay_api_key,
            "q": query,
            "image_type": "photo",
            "per_page": 3,
            "safesearch": "true",
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("hits"):
                return data["hits"][0]["webformatURL"]
        except Exception as e:
            print(f"Pixabay error: {e}")
        return None
