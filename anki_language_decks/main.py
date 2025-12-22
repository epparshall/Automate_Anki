# anki_language_decks/main.py
import os
from dotenv import load_dotenv

from .anki_client import AnkiClient
from .deck_builder import DeckBuilder
from .csv_loader import load_csv_data
from .config.languages import LANGUAGES

load_dotenv()

def main():
    anki = AnkiClient()
    pixabay_key = os.getenv("PIXABAY_API_KEY")

    if not pixabay_key:
        print("⚠️  No PIXABAY_API_KEY in .env – images will be skipped.")
    else:
        print("✓ Pixabay API key loaded – will fetch images.")

    # Now correctly passing the new parameter
    builder = DeckBuilder(anki, pixabay_key, skip_existing_decks=True)

    built_count = 0
    for language, config in LANGUAGES.items():
        lang_code = config["code"]
        subdecks = config.get("subdecks", {})

        print(f"\n📚 Processing {language} ({lang_code})...")

        if "IPA" in subdecks:
            cfg = subdecks["IPA"]
            cards = load_csv_data(cfg["csv_folder"], cfg["csv_file"], cfg["required_columns"])
            builder.build_ipa_deck(language, cards, lang_code)
            built_count += 1

        if "Pronunciation Rules" in subdecks:
            cfg = subdecks["Pronunciation Rules"]
            cards = load_csv_data(cfg["csv_folder"], cfg["csv_file"], cfg["required_columns"])
            builder.build_pronunciation_rules_deck(language, cards, lang_code)
            built_count += 1

        # Add more deck types here later

    print(f"\n✅ Done! Processed {built_count} deck type(s). Existing decks were skipped automatically.")

if __name__ == "__main__":
    main()
