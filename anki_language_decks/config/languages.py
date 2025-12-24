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
                "builder": "ipa",
            },
        }
    },
    "English (British)": {
        "code": "en-gb",
        "subdecks": {
            "IPA": {
                "csv_folder": "data/ipa_card_data",
                "csv_file": "british_english_ipa_cards.csv",
                "required_columns": ["ipa", "description", "example_word", "english_translation", "word_ipa"],
                "builder": "ipa",
            },
        }
    },
    "Spanish": {
        "code": "es",
        "subdecks": {
            "IPA": {
                "csv_folder": "data/ipa_card_data",
                "csv_file": "spanish_ipa_cards.csv",
                "required_columns": ["ipa", "description", "example_word", "english_translation", "word_ipa"],
                "builder": "ipa",
            },
        }
    },
    "German": {
        "code": "de",
        "subdecks": {
            "IPA": {
                "csv_folder": "data/ipa_card_data",
                "csv_file": "german_ipa_cards.csv",
                "required_columns": ["ipa", "description", "example_word", "english_translation", "word_ipa"],
                "builder": "ipa",
            },
        }
    },
    "Russian": {
        "code": "ru",
        "subdecks": {
            "IPA": {
                "csv_folder": "data/ipa_card_data",
                "csv_file": "russian_ipa_cards.csv",
                "required_columns": ["ipa", "description", "example_word", "english_translation", "word_ipa"],
                "builder": "ipa",
            },
        }
    },
}
