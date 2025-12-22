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
            print(f"    Downloading from: {path_or_url[:80]}...")
            response = requests.get(path_or_url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Failed to download file from URL: {path_or_url}")
            data_bytes = response.content
            print(f"    Downloaded {len(data_bytes)} bytes")

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
        if not is_audio and len(data_bytes) < 500:
            raise ValueError(
                f"Downloaded data too small ({len(data_bytes)} bytes), likely not an image"
            )

        data_b64 = base64.b64encode(data_bytes).decode("utf-8")

        # Store in Anki
        stored_filename = self._invoke(
            "storeMediaFile", {"filename": filename, "data": data_b64}
        )
        print(f"    Stored in Anki as: {stored_filename}")

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
    """Helper class to get audio and images from Pixabay"""

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
    def get_image(query: str, pixabay_api_key: str) -> Optional[str]:
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
    ipa_cards: List[Tuple[str, str, str, str]],
    language_code: str,
    pixabay_api_key: Optional[str] = None,
):
    """
    Build an IPA deck with audio pronunciations and images.

    Args:
        client: AnkiClient instance
        deck_name: Name of the deck to create
        ipa_cards: List of tuples (IPA symbol, description, example word, English translation)
        language_code: Language code for TTS (e.g., 'fr', 'es', 'de', 'it')
        pixabay_api_key: Optional Pixabay API key for images
    """

    client.ensure_deck_exists(deck_name)
    media_helper = MediaHelper()

    for ipa, description, example_word, english_translation in ipa_cards:
        front = f"{ipa}"
        back = f"{description}<br><b>Example:</b> {example_word}"

        # Generate TTS audio
        print(f"Generating TTS for '{example_word}'...")
        audio_path = media_helper.generate_tts_audio(example_word, language_code)
        print("  ✓ Generated TTS audio")

        # Get image using English translation
        image_url = None
        if pixabay_api_key:
            print(f"  Fetching image for '{english_translation}'...")
            image_url = media_helper.get_image(english_translation, pixabay_api_key)

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
    # Install required packages first: pip install gtts python-dotenv requests

    # French IPA cards
    french_ipa_cards = [
        # Vowels
        (
            "[i]",
            "Tongue high and front, lips spread, mouth nearly closed",
            "lit",
            "bed",
        ),
        ("[e]", "Tongue mid-high and front, lips slightly spread", "café", "coffee"),
        (
            "[ɛ]",
            "Tongue mid-low and front, mouth more open, lips spread",
            "forêt",
            "forest",
        ),
        ("[a]", "Tongue low and front, mouth wide open", "chat", "cat"),
        ("[ɑ]", "Tongue low and back, mouth wide open", "pâte", "dough"),
        (
            "[ɔ]",
            "Tongue mid-low and back, lips rounded, mouth half open",
            "porte",
            "door",
        ),
        (
            "[o]",
            "Tongue mid-high and back, lips rounded, mouth less open",
            "gâteau",
            "cake",
        ),
        ("[u]", "Tongue high and back, lips tightly rounded", "loup", "wolf"),
        ("[y]", "Tongue high and front (like [i]), lips rounded", "lune", "moon"),
        ("[ø]", "Tongue mid-high and front, lips rounded", "feu", "fire"),
        (
            "[œ]",
            "Tongue mid-low and front, lips rounded, mouth more open",
            "fleur",
            "flower",
        ),
        (
            "[ə]",
            "Tongue mid-central, relaxed, lips neutral (the schwa)",
            "cheval",
            "horse",
        ),
        # Nasal vowels
        (
            "[ɛ̃]",
            "Like [ɛ] but air flows through nose, mouth half open",
            "pain",
            "bread",
        ),
        (
            "[ɑ̃]",
            "Like [ɑ] but air flows through nose, mouth wide open",
            "blanc",
            "white",
        ),
        ("[ɔ̃]", "Like [ɔ] but air flows through nose, lips rounded", "pont", "bridge"),
        (
            "[œ̃]",
            "Like [œ] but air flows through nose, lips rounded",
            "parfum",
            "perfume",
        ),
        # Plosives (stops)
        (
            "[p]",
            "Close lips, build pressure, release without vocal cords",
            "pain",
            "bread",
        ),
        ("[b]", "Close lips, build pressure, release with vocal cords", "bois", "wood"),
        (
            "[t]",
            "Tongue touches ridge behind teeth, release without vocal cords",
            "table",
            "table",
        ),
        (
            "[d]",
            "Tongue touches ridge behind teeth, release with vocal cords",
            "dent",
            "tooth",
        ),
        (
            "[k]",
            "Back of tongue touches soft palate, release without vocal cords",
            "café",
            "coffee",
        ),
        (
            "[g]",
            "Back of tongue touches soft palate, release with vocal cords",
            "gare",
            "station",
        ),
        # Fricatives
        (
            "[f]",
            "Upper teeth touch lower lip, air flows through without vocal cords",
            "fleur",
            "flower",
        ),
        (
            "[v]",
            "Upper teeth touch lower lip, air flows through with vocal cords",
            "verre",
            "glass",
        ),
        (
            "[s]",
            "Tongue near ridge behind teeth, air hisses through without vocal cords",
            "sel",
            "salt",
        ),
        (
            "[z]",
            "Tongue near ridge behind teeth, air hisses through with vocal cords",
            "zoo",
            "zoo",
        ),
        (
            "[ʃ]",
            "Tongue pulled back, lips rounded, air flows without vocal cords",
            "chapeau",
            "hat",
        ),
        (
            "[ʒ]",
            "Tongue pulled back, lips rounded, air flows with vocal cords",
            "jardin",
            "garden",
        ),
        # Nasals
        (
            "[m]",
            "Lips closed, air flows through nose with vocal cords",
            "maison",
            "house",
        ),
        (
            "[n]",
            "Tongue touches ridge behind teeth, air flows through nose with vocal cords",
            "nez",
            "nose",
        ),
        (
            "[ɲ]",
            "Tongue touches hard palate, air flows through nose with vocal cords",
            "montagne",
            "mountain",
        ),
        (
            "[ŋ]",
            "Back of tongue touches soft palate, air flows through nose with vocal cords",
            "parking",
            "parking",
        ),
        # Liquids
        (
            "[l]",
            "Tongue tip touches ridge behind teeth, air flows around sides",
            "lune",
            "moon",
        ),
        (
            "[ʁ]",
            "Back of tongue near uvula, creates friction with vocal cords",
            "rouge",
            "red",
        ),
        # Approximants
        (
            "[j]",
            "Tongue high and front near palate but not touching, with vocal cords",
            "pied",
            "foot",
        ),
        (
            "[w]",
            "Lips rounded, tongue high and back, glides to vowel with vocal cords",
            "roi",
            "king",
        ),
        (
            "[ɥ]",
            "Lips rounded, tongue high and front, glides to vowel with vocal cords",
            "huile",
            "oil",
        ),
    ]

    # Spanish IPA cards example
    spanish_ipa_cards = [
        ("[a]", "Open central vowel", "casa", "house"),
        ("[e]", "Close-mid front unrounded vowel", "peso", "weight"),
        ("[i]", "Close front unrounded vowel", "piso", "floor"),
        ("[o]", "Close-mid back rounded vowel", "como", "how"),
        ("[u]", "Close back rounded vowel", "luna", "moon"),
        ("[p]", "Voiceless bilabial plosive", "peso", "weight"),
        ("[b]", "Voiced bilabial plosive", "boca", "mouth"),
        ("[t]", "Voiceless alveolar plosive", "taza", "cup"),
        ("[d]", "Voiced alveolar plosive", "dedo", "finger"),
        ("[k]", "Voiceless velar plosive", "casa", "house"),
        ("[g]", "Voiced velar plosive", "gato", "cat"),
        ("[tʃ]", "Voiceless postalveolar affricate", "chico", "boy"),
        ("[f]", "Voiceless labiodental fricative", "flor", "flower"),
        ("[s]", "Voiceless alveolar fricative", "sol", "sun"),
        ("[x]", "Voiceless velar fricative", "joven", "young"),
        ("[m]", "Bilabial nasal", "madre", "mother"),
        ("[n]", "Alveolar nasal", "noche", "night"),
        ("[ɲ]", "Palatal nasal", "año", "year"),
        ("[l]", "Alveolar lateral approximant", "lado", "side"),
        ("[ʎ]", "Palatal lateral approximant", "llave", "key"),
        ("[r]", "Alveolar tap", "pero", "but"),
        ("[r̄]", "Alveolar trill", "perro", "dog"),
        ("[j]", "Palatal approximant", "bien", "well"),
        ("[w]", "Labial-velar approximant", "bueno", "good"),
    ]

    anki = AnkiClient("http://localhost:8765")

    # Load API key from environment variable
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

    if not PIXABAY_API_KEY:
        print("⚠️  Warning: PIXABAY_API_KEY not found in .env file")
        print("   Images will be skipped. Add your key to .env to enable images.")
        print("   Get a free key at: https://pixabay.com/api/docs/\n")

    # Delete existing deck to get fresh images (optional)
    # Uncomment these lines to delete and recreate the deck:
    try:
        anki._invoke(
            "deleteDecks",
            {"decks": ["French IPA with Audio & Images"], "cardsToo": True},
        )
        print("🗑️  Deleted existing deck")
    except:
        pass

    build_ipa_deck(
        client=anki,
        deck_name="French IPA with Audio & Images",
        ipa_cards=french_ipa_cards,
        language_code="fr",
        pixabay_api_key=PIXABAY_API_KEY,
    )

    # Uncomment to build Spanish deck too!
    # build_ipa_deck(
    #     client=anki,
    #     deck_name="Spanish IPA with Audio & Images",
    #     ipa_cards=spanish_ipa_cards,
    #     language_code="es",
    #     pixabay_api_key=PIXABAY_API_KEY,
    # )

    print("\n✓ Done! Open Anki desktop and sync.")
