# src/advanced_analyzer.py

from src.analyzer import TextAnalyzer
from collections import Counter
import os

class AdvancedTextAnalyzer(TextAnalyzer):
    def __init__(self, filepaths):
        # filepaths can be a single file or a list
        if isinstance(filepaths, str):
            self.filepaths = [filepaths]
        else:
            self.filepaths = filepaths
        self.text = ""
        self.words = []
        self.sentences = []

    def load_text(self):
        combined_text = ""
        for path in self.filepaths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{path} does not exist")
            with open(path, "r", encoding="utf-8") as f:
                combined_text += f.read() + " "
        self.text = combined_text.strip()
        self.sentences = [s.strip() for s in self.text.split('.') if s]
        self.words = [w.strip(".,!?;:").lower() for w in self.text.split()]

    def unique_words_count(self):
        return len(set(self.words))

    def most_common_letters(self, n=5):
        letters = [c.lower() for c in self.text if c.isalpha()]
        counter = Counter(letters)
        return counter.most_common(n)

    def analyze(self):
        self.load_text()
        print(f"Characters: {len(self.text)}")
        print(f"Words: {len(self.words)}")
        print(f"Sentences: {len(self.sentences)}")
        print(f"Unique Words: {self.unique_words_count()}")
        print(f"Most common words: {Counter(self.words).most_common(5)}")
        print(f"Most common letters: {self.most_common_letters()}")
