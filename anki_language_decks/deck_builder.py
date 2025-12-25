# deck_builder.py
import re
from typing import List, Dict, Optional

from .anki_client import AnkiClient
from .media_helper import MediaHelper


class DeckBuilder:
    def __init__(
        self,
        anki_client: AnkiClient,
        pixabay_key: Optional[str] = None,
        skip_existing_decks: bool = True,
    ):
        self.anki = anki_client
        self.media = MediaHelper()
        self.pixabay_key = pixabay_key
        self.skip_existing_decks = skip_existing_decks

    def _deck_has_notes(self, deck_name: str) -> bool:
        """Check if the deck already contains any notes."""
        note_ids = self.anki._invoke("findNotes", {"query": f'deck:"{deck_name}"'})
        return len(note_ids) > 0

    def build_ipa_deck(self, language: str, cards: List[Dict[str, str]], lang_code: str):
        deck_name = f"{language}::IPA"
        self.anki.ensure_deck(deck_name)

        if self.skip_existing_decks and self._deck_has_notes(deck_name):
            print(f"   → Skipping {deck_name} (already has notes)")
            return

        print(f"   → Building {deck_name} ({len(cards)} cards)")
        processed_fronts = set()

        for card in cards:
            front = f"<big>{card['ipa']}</big>"
            if front in processed_fronts:
                continue
            processed_fronts.add(front)

            back = (
                f"<b>Example:</b> {card['example_word']} <big>{card['word_ipa']}</big><br><br>"
                f"{card['description']}<br><br>"
                f"<i>English:</i> {card['english_translation']}"
            )

            audio_path = self.media.generate_tts_audio(card['example_word'], lang_code)
            image_url = self.media.get_image(card['english_translation'], self.pixabay_key or "")

            self.anki.add_note(
                deck_name=deck_name,
                front=front,
                back=back,
                back_image=image_url,
                back_audio=audio_path,
                tags=[language.lower().replace(' ', '-'), "ipa"],
            )

    def build_pronunciation_rules_deck(self, language: str, cards: List[Dict[str, str]], lang_code: str):
        deck_name = f"{language}::Pronunciation Rules"
        self.anki.ensure_deck(deck_name)

        if self.skip_existing_decks and self._deck_has_notes(deck_name):
            print(f"   → Skipping {deck_name} (already has notes)")
            return

        print(f"   → Building {deck_name} ({len(cards)} cards)")
        processed_fronts = set()

        for card in cards:
            front = card["rule"]
            if front in processed_fronts:
                continue
            processed_fronts.add(front)
            
            back = card["explanation"]

            example_word = card.get("example_word")
            if example_word:
                back += f"<br><br><b>Example:</b> {example_word}"
                if card.get("example_ipa"):
                    back += f" → {card['example_ipa']}"

            audio_path = self.media.generate_tts_audio(example_word, lang_code) if example_word else None
            image_url = self.media.get_image(card.get("image_query", ""), self.pixabay_key or "")

            self.anki.add_note(
                deck_name=deck_name,
                front=front,
                back=back,
                back_image=image_url,
                back_audio=audio_path,
                tags=[language.lower().replace(' ', '-'), "pronunciation"],
            )

    def build_vocabulary_deck(self, language: str, cards: List[Dict[str, str]], lang_code: str):
        deck_name = f"{language}::Basic Vocabulary"
        self.anki.ensure_deck(deck_name)

        if self.skip_existing_decks and self._deck_has_notes(deck_name):
            print(f"   → Skipping {deck_name} (already has notes)")
            return

        print(f"   → Building {deck_name} ({len(cards)} cards)")
        processed_fronts = set()

        for card in cards:
            word_with_suffix = card["word"]
            
            front = word_with_suffix
            if front in processed_fronts:
                continue
            processed_fronts.add(front)
            
            translation = card["translation"]
            sentence = card.get("example_sentence", "")
            
            clean_word = re.sub(r'\s*\([^)]*\)$', '', word_with_suffix).strip()

            back = f"<b>{translation}</b>"
            if sentence:
                back += f"<br><br><i>Example:</i> {sentence}"

            audio_path = self.media.generate_tts_audio(clean_word, lang_code)
            image_url = self.media.get_image(translation, self.pixabay_key or "")

            self.anki.add_note(
                deck_name=deck_name,
                front=front,
                back=back,
                back_image=image_url,
                back_audio=audio_path,
                tags=[language.lower().replace(' ', '-'), "vocabulary"],
            )