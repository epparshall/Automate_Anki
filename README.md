# Anki Language Deck Builder

**Automated creation of rich, media-enhanced Anki decks for any language**

This tool lets you generate high-quality Anki flashcards for **any language** you want to learn. Out of the box, it includes full support for **French** (with Spanish ready to enable), but the modular design makes adding new languages simple.

Supported deck types:
- **IPA Phonetics** . Master individual sounds with articulation tips
- **Pronunciation Rules** . Essential rules for authentic pronunciation
- **Basic Vocabulary** . High-frequency words (perfect for the famous “top 625 words” deck)

Every card includes:
- Clean, styled HTML formatting
- Native-speaker **audio** (Google TTS)
- Relevant **images** (via Pixabay API)
- Automatic tagging and **nested deck organization** (e.g., `French::IPA`, `Japanese::Pronunciation Rules`)

Cards are added directly to Anki using **AnkiConnect** . No manual import needed.

---

## Features

- **Language-Agnostic & Config-Driven** . Add any language or deck type via `config/languages.py`
- **Smart Skipping** . Automatically skips decks that already exist in Anki
- **Automatic Media** . TTS audio + high-quality image search
- **Duplicate Handling** . Updates existing notes and prevents duplicates
- **Nested Decks** . Clean hierarchy for multiple languages and deck types
- **Highly Extensible** . New languages, cloze cards, custom note types

---

## Project Structure

```
anki-language-deck-builder/
├── run.py                          # Easy launcher (run this)
├── .env                            # PIXABAY_API_KEY (optional)
├── data/
│   ├── ipa_card_data/
│   │   └── french_ipa_cards.csv
│   ├── pronunciation_rules/
│   │   └── french_rules.csv
│   └── vocabulary/
└── anki_language_decks/
    ├── __init__.py
    ├── main.py
    ├── anki_client.py
    ├── deck_builder.py
    ├── media_helper.py
    ├── csv_loader.py
    └── config/
        └── languages.py
```

---

## Requirements

- **Python 3.8+**
- **Anki** running with **AnkiConnect** enabled  
  (default: `http://localhost:8765`)
- Install dependencies:

```bash
pip install -r requirements.txt
```

Optional:
- Free Pixabay API key from pixabay.com/api/docs

---

## Setup

1. Install Anki and enable the AnkiConnect add-on.
2. Start Anki.
3. (Optional) Create a `.env` file in the project root:

```env
PIXABAY_API_KEY=your_key_here
```

Images are skipped if no key is provided.

---

## Usage

From the project root, run:

```bash
python run.py
```

- First run . Builds all configured decks
- Subsequent runs . Skips existing decks automatically (very fast)
- To force a full rebuild . Set `skip_existing_decks = False` in `main.py`

Open Anki and sync. Your nested decks will appear.

---

## Adding New Languages or Decks

All configuration lives in:

```
anki_language_decks/config/languages.py
```

Example . Adding a Japanese pronunciation rules deck:

```python
"Japanese": {
    "code": "ja",
    "subdecks": {
        "Pronunciation Rules": {
            "csv_folder": "data/pronunciation_rules",
            "csv_file": "japanese_rules.csv",
            "required_columns": [
                "rule",
                "explanation",
                "example_word",
                "example_ipa",
                "image_query"
            ],
        }
    }
}
```

Create the corresponding CSV in `data/` and run the script again.

---

## Example Card Layouts

### IPA Card (any language)

Front:
```
[ʁ]
```

Back:
```
Example: rouge [ʁuʒ]
Tongue back, uvular fricative (gargle-like)
English: red
[Image] [Audio]
```

### Pronunciation Rules Card

Front:
```
Nasal vowels
```

Back:
```
Vowels before N/M are nasalized
Example: bon → [bɔ̃]
[Image] [Audio]
```

### Vocabulary Card

Front:
```
chat
```

Back:
```
cat
Example: Le chat dort.
[Image] [Audio]
```

---

## Notes & Tips

- All media is embedded directly in Anki
- Google gTTS is reliable for most languages
- Image quality depends on Pixabay results
- To rebuild decks . Delete in Anki or disable skipping
- Full UTF-8 support, including IPA symbols

---

## License

MIT License . Feel free to use, modify, and share.

Happy language learning 🌍✨
