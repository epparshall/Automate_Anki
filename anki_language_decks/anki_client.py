# anki_client.py
import base64
import os
import requests
from typing import Optional, List
from urllib.parse import urlparse

class AnkiClient:
    def __init__(self, url: str = "http://localhost:8765"):
        self.url = url
        self.version = 6

    def _invoke(self, action: str, params: dict | None = None):
        payload = {"action": action, "version": self.version, "params": params or {}}
        resp = requests.post(self.url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(data["error"])
        return data["result"]

    def ensure_deck(self, deck_name: str):
        self._invoke("createDeck", {"deck": deck_name})

    def _store_media(self, path_or_url: str, is_audio: bool = False) -> str:
        if path_or_url.startswith(("http://", "https://")):
            resp = requests.get(path_or_url, timeout=10)
            resp.raise_for_status()
            data = resp.content
            filename = os.path.basename(urlparse(path_or_url).path) or f"media_{hash(path_or_url)}.bin"
        else:
            if not os.path.exists(path_or_url):
                raise FileNotFoundError(path_or_url)
            with open(path_or_url, "rb") as f:
                data = f.read()
            filename = os.path.basename(path_or_url)

        b64 = base64.b64encode(data).decode()
        stored_name = self._invoke("storeMediaFile", {"filename": filename, "data": b64})
        return f"[sound:{stored_name}]" if is_audio else f'<img src="{stored_name}">'

    def add_note(
        self,
        deck_name: str,
        front: str,
        back: str,
        tags: Optional[List[str]] = None,
        front_image: Optional[str] = None,
        back_image: Optional[str] = None,
        front_audio: Optional[str] = None,
        back_audio: Optional[str] = None,
    ):
        # Build fields with media
        front_html = front
        back_html = back

        if front_image:
            front_html += "<br>" + self._store_media(front_image)
        if back_image:
            back_html += "<br>" + self._store_media(back_image)
        if front_audio:
            front_html += self._store_media(front_audio, is_audio=True)
        if back_audio:
            back_html += self._store_media(back_audio, is_audio=True)

        # Check for duplicate on a per-language basis
        escaped = front.replace('"', '\\"')
        language_tag = (tags or [""])[0]
        query = f'tag:{language_tag} "Front:{escaped}"'
        
        existing = self._invoke("findNotes", {"query": query})
        if existing:
            print(f'Skipping duplicate: "{front[:50]}"')
            return

        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {"Front": front_html, "Back": back_html},
            "tags": tags or [],
            "options": {"allowDuplicate": False},
        }
        self._invoke("addNote", {"note": note})
        print(f'Added: "{front[:50]}"')