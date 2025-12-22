# config/languages.py
from typing import Dict

LANGUAGES: Dict[str, Dict] = {
    "French": {
        "code": "fr",
        "subdecks": {
            "IPA": {
                "csv_folder": "data/ipa_card_data",
                "csv_file": "french_ipa_cards.csv",
                "required_columns": ["ipa", "description", "example_word", "english_translation", "word_ipa"],
                "builder": "ipa",  # optional: makes it explicit which builder to use
            },
            "Pronunciation Rules": {
                "csv_folder": "data/pronunciation_rules",
                "csv_file": "french_rules.csv",
                "required_columns": ["rule", "explanation", "example_word", "example_ipa", "image_query"],
                "builder": "pronunciation_rules",
            },
            # You can uncomment and add this later when ready
            # "Basic Vocabulary": {
            #     "csv_folder": "data/vocabulary",
            #     "csv_file": "french_top_625.csv",
            #     "required_columns": ["word", "translation", "example_sentence"],
            #     "builder": "vocabulary",
            # },
        }
    },
    # Add more languages here in the future, e.g.:
    # "Spanish": {
    #     "code": "es",
    #     "subdecks": { ... }
    # },
}
