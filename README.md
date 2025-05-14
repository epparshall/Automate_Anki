# Automate Anki
I created this project to automate the flashcard making process in Anki.

## Instructions
1. Install Anki Connect [here](https://ankiweb.net/shared/info/2055492159).<br>
2. Create an Anki_Automate object using the line `anki_obj = Anki_Automate(deck_name=deck_name, connect_url=url)` where `deck_name` is a previously created deck, and `url` is the Anki Connect URL (by default `http://localhost:8765`).<br>
3. Add a flashcard using the line `anki_obj.add_flashcard(front, back)` where `front` and `back` are strings of what should be on the card.<br>
4. To add images or audio, call the functions `anki_obj.get_image_str(image_path)` and `anki_obj.get_audio_str(sound_path)` respectively. Both functions will return a string that is to be added to the `front` or `back` parameter of the `add_flashcard` function.<br>
5. After running the code, be sure to click `sync` within Anki.
