import base64
import os
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests


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
        # Determine filename
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            response = requests.get(path_or_url)
            if response.status_code != 200:
                raise ValueError(f"Failed to download file from URL: {path_or_url}")
            filename = os.path.basename(urlparse(path_or_url).path)
            data_bytes = response.content
        else:
            if not os.path.exists(path_or_url):
                raise ValueError(f"File does not exist: {path_or_url}")
            filename = os.path.basename(path_or_url)
            with open(path_or_url, "rb") as f:
                data_bytes = f.read()

        # Encode to base64 and upload to Anki media
        data_b64 = base64.b64encode(data_bytes).decode("utf-8")
        self._invoke("storeMediaFile", {"filename": filename, "data": data_b64})

        if is_audio:
            return f"[sound:{filename}]"
        else:
            return f'<img src="{filename}">'

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
    ):
        # --- APPEND MEDIA FIRST ---
        if front_image:
            front += "<br>" + self._get_media_str(front_image, is_audio=False)
        if back_image:
            back += "<br>" + self._get_media_str(back_image, is_audio=False)
        if front_audio:
            front += "<br>" + self._get_media_str(front_audio, is_audio=True)
        if back_audio:
            back += "<br>" + self._get_media_str(back_audio, is_audio=True)

        # --- DUPLICATE CHECK (after media is appended) ---
        # Escape quotes in the search query
        front_escaped = front.replace('"', '\\"')
        back_escaped = back.replace('"', '\\"')
        existing_notes = self._invoke(
            "findNotes", {"query": f'deck:"{deck_name}" front:"{front_escaped}"'}
        )
        if existing_notes:
            print(f'Note with front "{front[:50]}..." already exists, skipping.')
            return

        # --- ADD NOTE ---
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {"Front": front, "Back": back},
            "options": {"allowDuplicate": False},
            "tags": tags or [],
        }

        try:
            self._invoke("addNote", {"note": note})
            print(f'Added note: "{front[:50]}..."')
        except RuntimeError as e:
            if "duplicate" in str(e).lower():
                print(f'Note already exists (duplicate detected): "{front[:50]}..."')
            else:
                raise


def build_basic_deck(
    client: AnkiClient,
    deck_name: str,
    cards: List[
        Tuple[
            str,  # front text
            str,  # back text
            Optional[str],  # front image
            Optional[str],  # back image
            Optional[str],  # front audio
            Optional[str],  # back audio
        ]
    ],
):
    """cards: list of tuples (front, back, front_image, back_image, front_audio, back_audio)"""
    client.ensure_deck_exists(deck_name)
    for front, back, f_img, b_img, f_audio, b_audio in cards:
        client.add_basic_note(deck_name, front, back, f_img, b_img, f_audio, b_audio)


if __name__ == "__main__":
    DECK_NAME = "French IPA (Audio+Images Demo)"

    # Example cards with optional media
    cards = [
        # Basic text only
        ("[r]", "Alveolar trill. Example: carro", None, None, None, None),
        # Text + front image
        (
            "[a]",
            "Open front unrounded vowel. Example: chat",
            "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_1280.jpg",
            None,
            None,
            None,
        ),
        # Text + front audio
        (
            "[y]",
            "Close front rounded vowel. Example: lune",
            None,
            None,
            "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3",
            None,
        ),
        # Text + both front image + front audio
        (
            "[o]",
            "Close-mid back rounded vowel. Example: pomme",
            "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_1280.jpg",
            None,
            "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3",
            None,
        ),
    ]

    anki = AnkiClient("http://localhost:8765")
    build_basic_deck(anki, DECK_NAME, cards)

    print("Done. Open Anki desktop and sync.")
