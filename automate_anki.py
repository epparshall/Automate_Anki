import base64
import os
import tempfile
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from gtts import gTTS

# Load environment variables from .env file
load_dotenv()


class AnkiClient:
    def __init__(self, connect_url: str = "http://localhost:8765"):
        self.url = connect_url
        self.version = 6

    def _invoke(self, action: str, params: dict | None = None):
        payload = {"action": action, "version": self.version, "params": params or {}}
        resp = requests.post(self.url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(data["error"])
        return data["result"]

    def ensure_deck_exists(self, deck_name: str):
        self._invoke("createDeck", {"deck": deck_name})

    def _get_media_str(self, path_or_url: str, is_audio=False) -> str:
        """Upload image or audio from local path or URL and return embed HTML/sound string"""
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            print(f"Downloading from: {path_or_url[:80]}...")
            response = requests.get(path_or_url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Failed to download file from URL: {path_or_url}")
            data_bytes = response.content
            print(f"Downloaded {len(data_bytes)} bytes")

            # Try to get filename from URL
            parsed = urlparse(path_or_url)
            filename = os.path.basename(parsed.path)
            if not filename or "." not in filename:
                # Fallback: determine extension from content-type
                content_type = response.headers.get("content-type", "")
                if "webp" in content_type:
                    ext = "webp"
                elif "png" in content_type:
                    ext = "png"
                elif "jpeg" in content_type or "jpg" in content_type:
                    ext = "jpg"
                elif "gif" in content_type:
                    ext = "gif"
                else:
                    ext = "jpg"  # safe fallback
                filename = f"media_{abs(hash(path_or_url))}.{ext}"
            else:
                # Ensure it has an extension; if not, add .jpg
                if "." not in filename:
                    filename += ".jpg"

        else:
            if not os.path.exists(path_or_url):
                raise ValueError(f"File does not exist: {path_or_url}")
            filename = os.path.basename(path_or_url)
            with open(path_or_url, "rb") as f:
                data_bytes = f.read()

        # For images: basic validation
        if not is_audio and len(data_bytes) < 500:  # raised threshold a bit
            raise ValueError(
                f"Downloaded data too small ({len(data_bytes)} bytes), likely not an image"
            )

        data_b64 = base64.b64encode(data_bytes).decode("utf-8")

        # Store in Anki
        stored_filename = self._invoke(
            "storeMediaFile", {"filename": filename, "data": data_b64}
        )
        print(f"Stored in Anki as: {stored_filename}")

        if is_audio:
            return f"[sound:{stored_filename}]"
        else:
            return f'<img src="{stored_filename}">'

    def add_basic_note(
        self,
        deck_name: str,
        front: str,
        back: str,
        front_image: Optional[str] = None,
        back_image: Optional[str] = None,
        front_audio: Optional[str] = None,
        back_audio: Optional[str] = None,
        tags: Optional[List[str]] = None,
        update_if_exists: bool = True,
    ):
        # Store original front text for searching
        original_front = front

        if front_image:
            front += "<br>" + self._get_media_str(front_image, is_audio=False)
        if back_image:
            back += "<br>" + self._get_media_str(back_image, is_audio=False)
        if front_audio:
            front += "<br>" + self._get_media_str(front_audio, is_audio=True)
        if back_audio:
            back += "<br>" + self._get_media_str(back_audio, is_audio=True)

        # Check if note already exists using original front text
        front_escaped = original_front.replace('"', '\\"')
        existing_notes = self._invoke(
            "findNotes", {"query": f'deck:"{deck_name}" front:"{front_escaped}*"'}
        )

        if existing_notes and update_if_exists:
            # Update existing note
            note_id = existing_notes[0]
            update_fields = {"Front": front, "Back": back}
            self._invoke(
                "updateNoteFields", {"note": {"id": note_id, "fields": update_fields}}
            )
            print(f'Updated note: "{original_front[:50]}..."')
            return
        elif existing_notes:
            print(
                f'Note with front "{original_front[:50]}..." already exists, skipping.'
            )
            return

        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {"Front": front, "Back": back},
            "options": {"allowDuplicate": False},
            "tags": tags or [],
        }

        try:
            self._invoke("addNote", {"note": note})
            print(f'Added note: "{original_front[:50]}..."')
        except RuntimeError as e:
            if "duplicate" in str(e).lower():
                print(f'Note already exists: "{original_front[:50]}..."')
            else:
                raise


class MediaHelper:
    """Helper class to get audio and images"""

    @staticmethod
    def generate_tts_audio(
        text: str, lang: str, output_path: Optional[str] = None
    ) -> str:
        """
        Generate pronunciation using Google TTS.

        Args:
            text: Text to convert to speech
            lang: Language code (e.g., 'fr' for French, 'es' for Spanish, 'de' for German)
            output_path: Optional path to save audio file

        Returns:
            Path to the generated audio file
        """
        if output_path is None:
            safe_text = "".join(c for c in text if c.isalnum())[:20]
            output_path = os.path.join(tempfile.gettempdir(), f"{lang}_{safe_text}.mp3")

        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        return output_path

    @staticmethod
    def get_unsplash_image(
        query: str, unsplash_access_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Get an image URL from Unsplash API.
        Requires free API key from: https://unsplash.com/developers

        Args:
            query: Search query for the image
            unsplash_access_key: Your Unsplash API access key

        Returns:
            URL of the image, or None if not found
        """
        if not unsplash_access_key:
            return None

        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {unsplash_access_key}"}
        params = {"query": query, "per_page": 1, "orientation": "landscape"}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                return data["results"][0]["urls"]["regular"]
        except Exception as e:
            print(f"Unsplash API error: {e}")
        return None

    @staticmethod
    def get_pexels_image(
        query: str, pexels_api_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Get an image URL from Pexels API (alternative to Unsplash).
        Requires free API key from: https://www.pexels.com/api/

        Args:
            query: Search query for the image
            pexels_api_key: Your Pexels API key

        Returns:
            URL of the image, or None if not found
        """
        if not pexels_api_key:
            return None

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": pexels_api_key}
        params = {"query": query, "per_page": 1, "orientation": "landscape"}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            if data.get("photos") and len(data["photos"]) > 0:
                return data["photos"][0]["src"]["large"]
        except Exception as e:
            print(f"Pexels API error: {e}")
        return None

    @staticmethod
    def get_pixabay_image(
        query: str, pixabay_api_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Get an image URL from Pixabay API.
        Requires free API key from: https://pixabay.com/api/docs/

        Args:
            query: Search query for the image
            pixabay_api_key: Your Pixabay API key

        Returns:
            URL of the image, or None if not found
        """
        if not pixabay_api_key:
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
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data.get("hits") and len(data["hits"]) > 0:
                return data["hits"][0]["webformatURL"]
        except Exception as e:
            print(f"Pixabay API error: {e}")
        return None


def build_ipa_deck(
    client: AnkiClient,
    deck_name: str,
    ipa_cards: List[Tuple[str, str, str]],
    language_code: str,
    image_api_key: Optional[str] = None,
    image_service: str = "pixabay",
):
    """
    Build an IPA deck with audio pronunciations and images.

    Args:
        client: AnkiClient instance
        deck_name: Name of the deck to create
        ipa_cards: List of tuples (IPA symbol, description, example word)
        language_code: Language code for TTS (e.g., 'fr', 'es', 'de', 'it')
        image_api_key: Optional API key for image service
        image_service: Which image service to use ('pixabay', 'pexels', or 'unsplash')
    """

    client.ensure_deck_exists(deck_name)
    media_helper = MediaHelper()

    for ipa, description, example_word in ipa_cards:
        front = f"{ipa}"
        back = f"{description}<br><b>Example:</b> {example_word}"

        # Generate TTS audio
        print(f"Generating TTS for '{example_word}'...")
        audio_path = media_helper.generate_tts_audio(example_word, language_code)
        print("  ✓ Generated TTS audio")

        # Get image
        image_url = None
        if image_api_key:
            print(f"Fetching image for '{example_word}'...")
            if image_service == "pixabay":
                image_url = media_helper.get_pixabay_image(example_word, image_api_key)
            elif image_service == "pexels":
                image_url = media_helper.get_pexels_image(example_word, image_api_key)
            elif image_service == "unsplash":
                image_url = media_helper.get_unsplash_image(example_word, image_api_key)

            if image_url:
                print("  ✓ Found image")
            else:
                print("  ✗ No image found")

        client.add_basic_note(
            deck_name=deck_name,
            front=front,
            back=back,
            back_image=image_url,
            back_audio=audio_path,
        )


if __name__ == "__main__":
    # Install required packages first: pip install gtts python-dotenv

    # French IPA cards
    french_ipa_cards = [
        ("[i]", "Close front unrounded vowel", "île"),
        ("[e]", "Close-mid front unrounded vowel", "été"),
        ("[ɛ]", "Open-mid front unrounded vowel", "être"),
        ("[a]", "Open front unrounded vowel", "chat"),
        ("[ɑ]", "Open back unrounded vowel", "pâte"),
        ("[ɔ]", "Open-mid back rounded vowel", "porte"),
        ("[o]", "Close-mid back rounded vowel", "eau"),
        ("[u]", "Close back rounded vowel", "tout"),
        ("[y]", "Close front rounded vowel", "lune"),
        ("[ø]", "Close-mid front rounded vowel", "deux"),
        ("[œ]", "Open-mid front rounded vowel", "neuf"),
        ("[ə]", "Mid central vowel (schwa)", "le"),
        ("[ɛ̃]", "Nasal open-mid front vowel", "pain"),
        ("[ɑ̃]", "Nasal open back vowel", "blanc"),
        ("[ɔ̃]", "Nasal open-mid back vowel", "pont"),
        ("[œ̃]", "Nasal open-mid front rounded vowel", "brun"),
        ("[p]", "Voiceless bilabial plosive", "pain"),
        ("[b]", "Voiced bilabial plosive", "beau"),
        ("[t]", "Voiceless alveolar plosive", "tête"),
        ("[d]", "Voiced alveolar plosive", "dans"),
        ("[k]", "Voiceless velar plosive", "coeur"),
        ("[g]", "Voiced velar plosive", "gare"),
        ("[f]", "Voiceless labiodental fricative", "feu"),
        ("[v]", "Voiced labiodental fricative", "vous"),
        ("[s]", "Voiceless alveolar fricative", "sel"),
        ("[z]", "Voiced alveolar fricative", "zéro"),
        ("[ʃ]", "Voiceless postalveolar fricative", "chat"),
        ("[ʒ]", "Voiced postalveolar fricative", "je"),
        ("[m]", "Bilabial nasal", "mer"),
        ("[n]", "Alveolar nasal", "nez"),
        ("[ɲ]", "Palatal nasal", "agneau"),
        ("[ŋ]", "Velar nasal", "parking"),
        ("[l]", "Alveolar lateral approximant", "lune"),
        ("[ʁ]", "Voiced uvular fricative", "rouge"),
        ("[j]", "Palatal approximant", "yeux"),
        ("[w]", "Labial-velar approximant", "oui"),
        ("[ɥ]", "Labial-palatal approximant", "huit"),
    ]

    # Spanish IPA cards example
    spanish_ipa_cards = [
        ("[a]", "Open central vowel", "casa"),
        ("[e]", "Close-mid front unrounded vowel", "peso"),
        ("[i]", "Close front unrounded vowel", "sí"),
        ("[o]", "Close-mid back rounded vowel", "como"),
        ("[u]", "Close back rounded vowel", "tú"),
        ("[p]", "Voiceless bilabial plosive", "peso"),
        ("[b]", "Voiced bilabial plosive", "boca"),
        ("[t]", "Voiceless alveolar plosive", "taza"),
        ("[d]", "Voiced alveolar plosive", "dedo"),
        ("[k]", "Voiceless velar plosive", "casa"),
        ("[g]", "Voiced velar plosive", "gato"),
        ("[tʃ]", "Voiceless postalveolar affricate", "chico"),
        ("[f]", "Voiceless labiodental fricative", "fácil"),
        ("[s]", "Voiceless alveolar fricative", "sol"),
        ("[x]", "Voiceless velar fricative", "joven"),
        ("[m]", "Bilabial nasal", "madre"),
        ("[n]", "Alveolar nasal", "noche"),
        ("[ɲ]", "Palatal nasal", "año"),
        ("[l]", "Alveolar lateral approximant", "lado"),
        ("[ʎ]", "Palatal lateral approximant", "llamar"),
        ("[r]", "Alveolar tap", "pero"),
        ("[r̄]", "Alveolar trill", "perro"),
        ("[j]", "Palatal approximant", "bien"),
        ("[w]", "Labial-velar approximant", "bueno"),
    ]

    anki = AnkiClient("http://localhost:8765")

    # Load API key from environment variable
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

    if not PIXABAY_API_KEY:
        print("⚠️  Warning: PIXABAY_API_KEY not found in .env file")
        print("   Images will be skipped. Add your key to .env to enable images.")
        print("   Get a free key at: https://pixabay.com/api/docs/\n")

    build_ipa_deck(
        client=anki,
        deck_name="French IPA with Audio & Images",
        ipa_cards=french_ipa_cards,
        language_code="fr",
        image_api_key=PIXABAY_API_KEY,
        image_service="pixabay",
    )

    # Uncomment to build Spanish deck too!
    # build_ipa_deck(
    #     client=anki,
    #     deck_name="Spanish IPA with Audio & Images",
    #     ipa_cards=spanish_ipa_cards,
    #     language_code="es",
    #     image_api_key=PIXABAY_API_KEY,
    #     image_service="pixabay"
    # )

    print("\n✓ Done! Open Anki desktop and sync.")
