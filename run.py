# run.py
"""
Simple launcher for the Anki Language Decks builder.
Run this from the project root with: python run.py
"""

import os
import sys

# Make sure Python can find our package
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the main function from the package
from anki_language_decks.main import main

if __name__ == "__main__":
    print("🚀 Starting Anki Language Deck Builder...\n")
    main()
    print("\n✅ All done! Open Anki to see your new decks.")