# src/analyzer.py

import os
from collections import Counter
import string
import pandas as pd  # for CSV export

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

    # ------------------- New Features -------------------
    def average_sentence_length(self):
        """Returns average number of words per sentence"""
        if not self.sentences:
            return 0
        return sum(len(s.split()) for s in self.sentences) / len(self.sentences)

    def letter_frequency(self, n=5):
        """Returns the n most common letters"""
        letters = [c.lower() for c in self.text if c.isalpha()]
        counter = Counter(letters)
        return counter.most_common(n)

    def save_to_csv(self, output_file="analysis.csv"):
        """Save analysis metrics to CSV"""
        df = pd.DataFrame({
            "Metric": ["Characters", "Words", "Sentences", "AvgSentenceLength"],
            "Count": [self.character_count(),
                      self.word_count(),
                      self.sentence_count(),
                      round(self.average_sentence_length(), 2)]
        })
        df.to_csv(output_file, index=False)
        print(f"Analysis saved to {output_file}")
    # -----------------------------------------------------

    def analyze(self):
        """Perform full analysis and print results"""
        self.load_text()
        print(f"Characters: {self.character_count()}")
        print(f"Words: {self.word_count()}")
        print(f"Sentences: {self.sentence_count()}")
        print(f"Average Sentence Length: {self.average_sentence_length():.2f} words")
        print("Most common words:", self.most_common_words())
        print("Most common letters:", self.letter_frequency())
        # Save results to CSV
        self.save_to_csv()
