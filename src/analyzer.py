# src/analyzer.py

import os
from collections import Counter
import string

class TextAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.text = ""
        self.words = []
        self.sentences = []

    def load_text(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"{self.filepath} does not exist")
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.text = f.read()
        self.sentences = [s.strip() for s in self.text.split('.') if s]
        self.words = [w.strip(string.punctuation).lower() for w in self.text.split()]

    def word_count(self):
        return len(self.words)

    def sentence_count(self):
        return len(self.sentences)

    def character_count(self):
        return len(self.text)

    def most_common_words(self, n=5):
        counter = Counter(self.words)
        return counter.most_common(n)

    def analyze(self):
        self.load_text()
        print(f"Characters: {self.character_count()}")
        print(f"Words: {self.word_count()}")
        print(f"Sentences: {self.sentence_count()}")
        print("Most common words:", self.most_common_words())
