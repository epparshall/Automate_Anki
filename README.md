# Anki Automate – Python Flashcard Creator

**Anki Automate** is a Python script to easily create Anki decks via **AnkiConnect**, making it simple to add flashcards programmatically. It is designed for **basic text-based decks**, fully compatible with **Anki Desktop, iOS, and AnkiWeb sync**.

---

## Features

- Add flashcards with **Front** and **Back** text fields.
- Works with **AnkiConnect** (local server) to push cards directly to Anki.
- Automatically avoids duplicate notes.
- Fully syncable to **iOS and AnkiWeb** decks.
- Lightweight and easy to extend for images or audio later.

---

## Requirements

- Python 3.8+  
- [Anki](https://apps.ankiweb.net/) installed on your computer  
- [AnkiConnect add-on](https://ankiweb.net/shared/info/2055492159) installed in Anki  
- `requests` and `pandas` Python libraries:

    pip install requests pandas

---

## Usage

1. Make sure **Anki** is running and **AnkiConnect** is installed.  
2. Update the script with your desired deck name:

    deck_name = "My Deck"
    anki_url = "http://localhost:8765"
    anki_obj = Anki_Automate(deck_name=deck_name, connect_url=anki_url)

3. Add flashcards:

    anki_obj.add_flashcard("Front text", "Back text")

4. Run the script:

    python anki_automate.py

5. Open Anki on your computer or iOS device. **Sync with AnkiWeb** to access your deck anywhere.

---

## Example

    from anki_automate import Anki_Automate

    deck_name = "French IPA"
    url = "http://localhost:8765"

    anki_obj = Anki_Automate(deck_name=deck_name, connect_url=url)
    anki_obj.add_flashcard("Front Example", "Back Example")

---

## Notes

- Currently supports **text-only flashcards**.  
- Future extensions can include **audio** or **images** for more complex decks.  
- Flashcards are **added directly to Anki**, so ensure Anki is running and AnkiConnect is accessible.

---

## License

MIT License
