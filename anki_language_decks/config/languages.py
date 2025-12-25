# config/languages.py
from typing import Dict, Any

# Common configuration for any pronunciation rules deck
PRONUNCIATION_RULES_CONFIG = {
    "csv_folder": "data/pronunciation_rules",
    "required_columns": ["rule", "explanation", "example_word", "example_ipa", "image_query"],
    "builder": "pronunciation_rules",
}

# Common configuration for any basic vocabulary deck
BASIC_VOCABULARY_CONFIG = {
    "csv_folder": "data/vocabulary",
    "required_columns": ["word", "translation", "example_sentence"],
    "builder": "vocabulary",
}


LANGUAGES: Dict[str, Dict[str, Any]] = {
    "French": {
        "name": "French",
        "native_name": "Français",
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
            "Basic Vocabulary": {
                **BASIC_VOCABULARY_CONFIG,
                "csv_file": "french_top_625.csv",
            },
        }
    },
    "English (British)": {
        "name": "English (British)",
        "native_name": "English (British)",
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
            "Basic Vocabulary": {
                **BASIC_VOCABULARY_CONFIG,
                "csv_file": "british_english_top_625.csv",
            },
        }
    },
    "Spanish": {
        "name": "Spanish",
        "native_name": "Español",
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
            "Basic Vocabulary": {
                **BASIC_VOCABULARY_CONFIG,
                "csv_file": "spanish_top_625.csv",
            },
        }
    },
    "German": {
        "name": "German",
        "native_name": "Deutsch",
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
            "Basic Vocabulary": {
                **BASIC_VOCABULARY_CONFIG,
                "csv_file": "german_top_625.csv",
            },
        }
    },
    "Russian": {
        "name": "Russian",
        "native_name": "Русский",
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
            "Basic Vocabulary": {
                **BASIC_VOCABULARY_CONFIG,
                "csv_file": "russian_top_625.csv",
            },
        }
    },
}
