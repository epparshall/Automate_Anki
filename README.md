# Anki IPA Deck Generator – French & Spanish Phonetics Flashcards

This Python script automatically creates rich Anki decks for learning **French** and **Spanish** IPA (International Phonetic Alphabet) symbols.  
Each flashcard focuses on a single IPA sound and includes:

- **Front**: The IPA symbol
- **Back**:
  - Articulation description (how to produce the sound)
  - Example word in the target language
  - Full IPA transcription of the example word (large and prominent)
  - High-quality image related to the English translation of the example word (via Pixabay)
  - Native pronunciation audio of the example word (via Google TTS)

Cards are added directly to Anki using **AnkiConnect** and are fully syncable across Anki Desktop, iOS, Android, and AnkiWeb.

---

## Features

- Modular data in easy-to-edit **CSV files**
- Automatic **TTS audio** generation (Google Text-to-Speech)
- Automatic **image fetching** from Pixabay (optional)
- Full **IPA transcription** displayed prominently
- Prevents duplicates and updates existing cards
- Clean HTML card layout
- Easily extensible to other languages

---

## Folder Structure

```
anki_ipa_deck/
├── main.py
├── data/
│   ├── french_ipa_cards.csv
│   └── spanish_ipa_cards.csv
└── .env
```

---

## Requirements

- Python 3.8+
- Anki (running)
- AnkiConnect add-on
- Python packages:

```bash
pip install requests python-dotenv gtts
```

Optional:
- Pixabay API key

---

## Setup

1. Install Anki and AnkiConnect.
2. Start Anki (AnkiConnect uses `http://localhost:8765`).
3. Optional `.env` file:

```env
PIXABAY_API_KEY=your_api_key_here
```

If missing, images are skipped.

---

## Usage

Run:

```bash
python main.py
```

- Builds **French IPA with Audio & Images**
- Uncomment Spanish section to build Spanish
- Optional deck deletion available in `main.py`

Sync Anki afterward.

---

## Customizing / Adding Languages

CSV columns:

- `ipa`
- `description`
- `example_word`
- `english_translation`
- `word_ipa`

Add a new CSV and wire it into `main.py`.

---

## Example Card Layout

Front:

```
[i]
```

Back:

```
Example: lit [li]
Tongue high and front, lips spread
[Image]
[Audio]
```

---

## Notes

- UTF-8 IPA fully supported
- No duplicate cards
- CSV fields with commas must be quoted
- Images depend on Pixabay search quality

---

## License

MIT License
