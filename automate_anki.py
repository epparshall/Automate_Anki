# main.py
import base64
import csv
import os
import tempfile
from typing import List, Tuple, Optional

from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from gtts import gTTS

# Load environment variables (.env file)
load_dotenv()

# ------------------------------------------------------------------
# Helper: Load cards from CSV
# ------------------------------------------------------------------
def load_ipa_cards(csv_filename: str) -> List[Tuple[str, str, str, str, str]]:
    """
    Load IPA cards from a CSV file in the data/ folder.
    Expected columns:
    ipa, description, example_word, english_translation, word_ipa
    """
    file_path = os.path.join(os.path.dirname(__file__), "ipa_card_data", csv_filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    cards = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # start=2 for better error messages
            try:
                cards.append((
                    row["ipa"].strip(),
                    row["description"].strip(),
                    row["example_word"].strip(),
                    row["english_translation"].strip(),
                    row["word_ipa"].strip(),  # Full IPA transcription of the example word
                ))
            except KeyError as e:
                raise ValueError(f"Missing column {e} in {csv_filename} at row {row_num}")

    print(f"Loaded {len(cards)} cards from {csv_filename}")
    return cards


# ------------------------------------------------------------------
# AnkiClient
# ------------------------------------------------------------------
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

            parsed = urlparse(path_or_url)
            filename = os.path.basename(parsed.path)
            if not filename or "." not in filename:
                content_type = response.headers.get("content-type", "")
                ext_map = {"webp": "webp", "png": "png", "jpeg": "jpg", "jpg": "jpg", "gif": "gif"}
                ext = next((v for k, v in ext_map.items() if k in content_type), "jpg")
                filename = f"media_{abs(hash(path_or_url))}.{ext}"
        else:
            if not os.path.exists(path_or_url):
                raise ValueError(f"File does not exist: {path_or_url}")
            filename = os.path.basename(path_or_url)
            with open(path_or_url, "rb") as f:
                data_bytes = f.read()

        if not is_audio and len(data_bytes) < 500:
            raise ValueError(f"Data too small ({len(data_bytes)} bytes), likely not an image")

        data_b64 = base64.b64encode(data_bytes).decode("utf-8")
        stored_filename = self._invoke(
            "storeMediaFile", {"filename": filename, "data": data_b64}
        )
        print(f"Stored in Anki as: {stored_filename}")
        return f"[sound:{stored_filename}]" if is_audio else f'<img src="{stored_filename}">'

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
        original_front = front
        if front_image:
            front += "<br>" + self._get_media_str(front_image, is_audio=False)
        if back_image:
            back += "<br>" + self._get_media_str(back_image, is_audio=False)
        if front_audio:
            front += "<br>" + self._get_media_str(front_audio, is_audio=True)
        if back_audio:
            back += "<br>" + self._get_media_str(back_audio, is_audio=True)

        front_escaped = original_front.replace('"', '\\"')
        existing_notes = self._invoke(
            "findNotes", {"query": f'deck:"{deck_name}" front:"{front_escaped}*"'}
        )

        if existing_notes and update_if_exists:
            note_id = existing_notes[0]
            self._invoke(
                "updateNoteFields",
                {"note": {"id": note_id, "fields": {"Front": front, "Back": back}}},
            )
            print(f'Updated note: "{original_front[:50]}..."')
            return
        elif existing_notes:
            print(f'Note already exists, skipping: "{original_front[:50]}..."')
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


# ------------------------------------------------------------------
# MediaHelper
# ------------------------------------------------------------------
class MediaHelper:
    @staticmethod
    def generate_tts_audio(text: str, lang: str, output_path: Optional[str] = None) -> str:
        if output_path is None:
            safe_text = "".join(c for c in text if c.isalnum())[:20]
            output_path = os.path.join(tempfile.gettempdir(), f"{lang}_{safe_text}.mp3")
        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        return output_path

    @staticmethod
    def get_image(query: str, pixabay_api_key: str) -> Optional[str]:
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
            if data.get("hits"):
                return data["hits"][0]["webformatURL"]
        except Exception as e:
            print(f"Pixabay API error: {e}")
        return None


# ------------------------------------------------------------------
# Build deck function
# ------------------------------------------------------------------
def build_ipa_deck(
    client: AnkiClient,
    deck_name: str,
    ipa_cards: List[Tuple[str, str, str, str, str]],
    language_code: str,
    pixabay_api_key: Optional[str] = None,
):
    client.ensure_deck_exists(deck_name)
    media_helper = MediaHelper()

    for ipa, description, example_word, english_translation, word_ipa in ipa_cards:
        front = f"{ipa}"

        # Back side: example word with its full IPA first, then pronunciation tip (description)
        back = (
            f"<b>Example:</b> {example_word} <span style='font-size: 150%;'>{word_ipa}</span><br><br>"
            f"{description}"
        )

        print(f"Generating TTS for '{example_word}'...")
        audio_path = media_helper.generate_tts_audio(example_word, language_code)
        print("✓ TTS generated")

        image_url = None
        if pixabay_api_key:
            print(f"Fetching image for '{english_translation}'...")
            image_url = media_helper.get_image(english_translation, pixabay_api_key)
            if image_url:
                print("✓ Image found")
            else:
                print("✗ No image found")

        client.add_basic_note(
            deck_name=deck_name,
            front=front,
            back=back,
            back_image=image_url,
            back_audio=audio_path,
        )


# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
if __name__ == "__main__":
    anki = AnkiClient("http://localhost:8765")

    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
    if not PIXABAY_API_KEY:
        print("⚠️ Warning: PIXABAY_API_KEY not found in .env file")
        print("Images will be skipped. Get a free key at https://pixabay.com/api/docs/")

    # Optional: delete existing decks before rebuilding
    # Uncomment the block below if you want to start fresh each time
    # for deck in ["French IPA with Audio & Images", "Spanish IPA with Audio & Images"]:
    #     try:
    #         anki._invoke("deleteDecks", {"decks": [deck], "cardsToo": True})
    #         print(f"Deleted deck: {deck}")
    #     except:
    #         pass

    # Build French deck
    french_cards = load_ipa_cards("french_ipa_cards.csv")
    build_ipa_deck(
        client=anki,
        deck_name="French IPA with Audio & Images",
        ipa_cards=french_cards,
        language_code="fr",
        pixabay_api_key=PIXABAY_API_KEY,
    )

    # Build Spanish deck (uncomment the lines below to enable it)
    # spanish_cards = load_ipa_cards("spanish_ipa_cards.csv")
    # build_ipa_deck(
    #     client=anki,
    #     deck_name="Spanish IPA with Audio & Images",
    #     ipa_cards=spanish_cards,
    #     language_code="es",
    #     pixabay_api_key=PIXABAY_API_KEY,
    # )

    print("\n✓ All done! Open Anki and sync to see your new deck(s).")
