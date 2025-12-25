# Anki Language Deck Builder

**Automated creation of rich, media-enhanced Anki decks for language learning.**

This tool automatically generates high-quality Anki flashcards for multiple languages and deck types. All cards are generated with native-speaker audio, relevant images, and are added directly to your Anki collection using AnkiConnect.

---

## Supported Decks

Out of the box, the following decks are configured and ready to be built:

| Language          | IPA Phonetics | Pronunciation Rules | Top 625 Vocabulary |
| ----------------- | :-----------: | :-----------------: | :----------------: |
| **English (GB)**  |       ✅       |          ✅          |         ✅         |
| **French**        |       ✅       |          ✅          |         ✅         |
| **Spanish**       |       ✅       |          ✅          |         ✅         |
| **German**        |       ✅       |          ✅          |         ✅         |
| **Russian**       |       ✅       |          ✅          |         ✅         |

---

## Features

- **Multi-Language & Multi-Deck**: Build decks for various languages and types, all defined in a single configuration file.
- **Rich Media**: Every card includes native-speaker audio (`Microsoft Edge TTS`) and relevant images (`Pixabay API`).
- **Smart Duplicate Handling**:
    - Uniqueness across languages is ensured by adding a language suffix (e.g., `(fr)`) to the front of cards.
    - Uniqueness within a single CSV is handled by skipping repeated entries during a run.
    - Uniqueness across multiple runs is handled by checking for existing notes in Anki (scoped by language tag) before adding.
- **Nested Decks**: Automatically organizes cards into a clean hierarchy (e.g., `French::IPA`, `Spanish::Basic Vocabulary`).
- **Direct Anki Integration**: Uses `AnkiConnect` to add and update cards directly. No manual CSV import required.
- **Extensible**: Designed to be easily extended with new languages or entirely new deck types.

---

## Requirements

- **Python 3.8+**
- **Anki** desktop application running with the **AnkiConnect** add-on installed and enabled.
- An internet connection for fetching media.
- A free **Pixabay API key** for image fetching (optional, but recommended).

---

## Setup

1.  **Install Anki & AnkiConnect**:
    - Download and install [Anki](https://apps.ankiweb.net/).
    - Open Anki, go to `Tools > Add-ons`, click `Get Add-ons...`, and paste the code `2055492159`.
    - Restart Anki.

2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up API Key (Optional)**:
    - Get a free API key from [pixabay.com/api/docs](https://pixabay.com/api/docs/).
    - Create a file named `.env` in the project root directory.
    - Add your API key to the `.env` file like this:
      ```
      PIXABAY_API_KEY=your_key_here
      ```
    - If no key is provided, images will be skipped.

---

## Usage

1.  Make sure Anki is open and running in the background.
2.  From the project root directory, run the script:
    ```bash
    python run.py
    ```
- **First run**: Builds all decks configured in `languages.py`.
- **Subsequent runs**: Automatically skips decks that already have notes, making it fast to run again.

---

## Customization

### Adding a New Language

To add a new language (e.g., Japanese), you would:
1.  Create the necessary CSV data files (e.g., `data/ipa_card_data/japanese_ipa_cards.csv`).
2.  Open `anki_language_decks/config/languages.py`.
3.  Add a new entry to the `LANGUAGES` dictionary:
    ```python
    "Japanese": {
        "name": "Japanese",
        "native_name": "日本語",
        "code": "ja", # Used for TTS
        "subdecks": {
            "IPA": {
                "csv_folder": "data/ipa_card_data",
                "csv_file": "japanese_ipa_cards.csv",
                "required_columns": ["ipa", "description", "example_word", "english_translation", "word_ipa"],
                "builder": "ipa",
            },
        }
    },
    ```
4.  Open `anki_language_decks/media_helper.py` and add the new language code and a corresponding TTS voice to the `generate_tts_audio` function.

### Adding a New Deck Type

To add a new deck type (e.g., "Grammar Rules"):
1.  Create your CSV data file (e.g., `data/grammar/french_grammar.csv`).
2.  Open `anki_language_decks/deck_builder.py` and add a new method, `build_grammar_deck`. This will contain the logic for how to format the front and back of your grammar cards.
3.  Open `anki_language_decks/main.py` and add a new `if "Grammar Rules" in subdecks:` block to the main loop to call your new builder method.

---

## Troubleshooting

**Error: `RuntimeError: cannot create note because it is a duplicate`**
-   This means Anki believes a card you're trying to add already exists.
-   **Cause**: This can happen if you have old versions of cards in your collection from previous runs, especially if the card format has changed.
-   **Solution**:
    1.  Open the Anki **Browser**.
    2.  Search for the cards causing the issue. For example, to find all IPA cards, you can search for `tag:ipa`. To find all French cards, search for `tag:french`.
    3.  Select all the conflicting cards and delete them.
    4.  Re-run the script.

---

## License
MIT License. Feel free to use, modify, and share.