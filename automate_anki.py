import requests
import json
import base64
import os
import pandas as pd

class Anki_Automate:
    def __init__(self, deck_name, connect_url):
        self.deck_name = deck_name
        self.ANKI_CONNECT_URL = connect_url
    
    def add_flashcard(self, front, back):

        '''
        Add a single flashcard to Anki with optional sound and image.
        
        Parameters:
            deck_name (str): The name of the deck to add the card to.
            front (str): The front side of the card.
            back (str): The back side of the card.
            sound_path (str, optional): Path to a sound file to include.
            image_path (str, optional): Path to an image file to include.
        '''


        payload = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": self.deck_name,
                    "modelName": "Basic",
                    "fields": {
                        "Front": front,
                        "Back": back
                    },
                    "options": {
                        "allowDuplicate": False
                    },
                    "tags": []
                }
            }
        }

        # Send a request to AnkiConnect to add the note
        response = requests.post(self.ANKI_CONNECT_URL, json=payload)
        result = response.json()
        
        if result.get("error"):
            print(f"Error adding note: {result['error']}")
        else:
            print("Note added successfully!") 
    
    def get_image_str(self, image_path):
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        media = [{
                "filename": image_path.split("/")[-1],
                "data": image_data
            }]

        if media:
            upload_payload = {
                "action": "storeMediaFile",
                "version": 6,
                "params": media[0]  # Handle one file at a time
            }
            response = requests.post(self.ANKI_CONNECT_URL, json=upload_payload)
            result = response.json()
            if result.get("error"):
                print(f"Error uploading media1: {result['error']}")

        # Embed image in the card
        return (f'<br><img src="{image_path.split("/")[-1]}">')

    def get_audio_str(self, sound_path):
        with open(sound_path, "rb") as sound_file:
                sound_data = base64.b64encode(sound_file.read()).decode("utf-8")

        media = [{
                "filename": sound_path.split("/")[-1],
                "data": sound_data
            }]

        if media:
            upload_payload = {
                "action": "storeMediaFile",
                "version": 6,
                "params": media[0]  # Handle one file at a time
            }
            response = requests.post(self.ANKI_CONNECT_URL, json=upload_payload)
            result = response.json()
            if result.get("error"):
                print(f"Error uploading media2: {result['error']}")

        # Embed image in the card
        return (f'<br>[sound:{sound_path.split("/")[-1]}]')

if __name__ == "__main__":
    # Example Usage
    deck_name = "French IPA"
    url = "http://localhost:8765"

    anki_obj = Anki_Automate(deck_name=deck_name, connect_url=url)
    media_path = "./French_IPA/Images/"
    file_names = os.listdir(media_path)
    df = pd.read_csv("./French_IPA/flashcards.csv")
    df = df.sort_values(by=df.columns[1], ascending=True)

    for row in range(len(df)):
        name_without_extension, extension = os.path.splitext(file_names[row])
        front = anki_obj.get_image_str("./French_IPA/Images/" + name_without_extension + ".jpg")
        back = f"{df.iloc[row, 0]} - {df.iloc[row, 1]} ({df.iloc[row, 2]}): {df.iloc[row, 3]} {anki_obj.get_audio_str('./French_IPA/Audio/' + name_without_extension + '.mp3')} {df.iloc[row, 4]}"
        anki_obj.add_flashcard(front, back)    

