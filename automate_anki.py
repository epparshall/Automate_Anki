from typing import List, Tuple

import requests


class AnkiClient:
    def __init__(self, connect_url: str = "http://localhost:8765"):
        self.url = connect_url
        self.version = 6

    def _invoke(self, action: str, params: dict | None = None):
        payload = {"action": action, "version": self.version, "params": params or {}}
        resp = requests.post(self.url, json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(data["error"])
        return data["result"]

    def ensure_deck_exists(self, deck_name: str):
        self._invoke("createDeck", {"deck": deck_name})

    def add_basic_note(
        self,
        deck_name: str,
        front: str,
        back: str,
        tags: List[str] | None = None,
    ):
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {
                "Front": front,
                "Back": back,
            },
            "options": {
                "allowDuplicate": False,
            },
            "tags": tags or [],
        }

        self._invoke("addNote", {"note": note})


def build_basic_deck(
    client: AnkiClient,
    deck_name: str,
    cards: List[Tuple[str, str]],
):
    client.ensure_deck_exists(deck_name)

    for front, back in cards:
        client.add_basic_note(deck_name, front, back)


if __name__ == "__main__":
    # ---- CONFIG ----
    DECK_NAME = "French IPA (MVP)"

    # Minimal example cards
    cards = [
        ("[r]", "Alveolar trill. Example: carro"),
        ("[ɾ]", "Alveolar tap. Example: caro"),
        ("[y]", "Close front rounded vowel. Example: lune"),
    ]

    # ---- RUN ----
    anki = AnkiClient("http://localhost:8765")
    build_basic_deck(anki, DECK_NAME, cards)

    print("Done. Open Anki desktop and sync.")
