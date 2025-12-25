# config/languages.py
from typing import Dict

# Common configuration for any pronunciation rules deck
PRONUNCIATION_RULES_CONFIG = {
    "csv_folder": "data/pronunciation_rules",
    "required_columns": ["rule", "explanation", "example_word", "example_ipa", "image_query"],
    "builder": "pronunciation_rules",
}

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
            "Pronunciation Rules": {
                **PRONUNCIATION_RULES_CONFIG,
                "csv_file": "french_rules.csv",
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
            "Pronunciation Rules": {
                **PRONUNCIATION_RULES_CONFIG,
                "csv_file": "british_english_rules.csv",
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
            "Pronunciation Rules": {
                **PRONUNCIATION_RULES_CONFIG,
                "csv_file": "spanish_rules.csv",
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
            "Pronunciation Rules": {
                **PRONUNCIATION_RULES_CONFIG,
                "csv_file": "german_rules.csv",
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
            "Pronunciation Rules": {
                **PRONUNCIATION_RULES_CONFIG,
                "csv_file": "russian_rules.csv",
            },
        }
    },
}