# csv_loader.py
import csv
import os
from typing import List, Dict

def load_csv_data(folder: str, filename: str, expected_columns: list[str]) -> List[Dict[str, str]]:
    """
    Generic CSV loader.
    Folder is relative to the project root (e.g., 'ipa_card_data').
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Go up from package
    file_path = os.path.join(base_dir, folder, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = set(expected_columns) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns {missing} in {filename}")

        cards = [{k: v.strip() for k, v in row.items()} for row in reader]

    print(f"Loaded {len(cards)} rows from {folder}/{filename}")
    return cards
