# src/analyzer.py
"""Core text analysis. Standard library only."""

import csv
import json
import os
import re
import string
from collections import Counter

from src.stopwords import STOPWORDS

SENTENCE_RE = re.compile(r"[^.!?]+[.!?]*")
WORD_RE = re.compile(r"[A-Za-z0-9']+")


def count_syllables(word):
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    if word.endswith("e") and not word.endswith(("le", "ee", "ye")) and len(word) > 3:
        word = word[:-1]
    groups = re.findall(r"[aeiouy]+", word)
    return max(1, len(groups))


class TextAnalyzer:
    def __init__(self, filepath):
        # Accept a single path or a list of paths.
        if isinstance(filepath, str):
            self.filepaths = [filepath]
        else:
            self.filepaths = list(filepath)
        self.text = ""
        self.words = []
        self.sentences = []
        self.paragraphs = []

    def _tokenize(self):
        self.sentences = [
            s.strip() for s in SENTENCE_RE.findall(self.text) if s.strip()
        ]
        self.words = [
            w.lower() for w in WORD_RE.findall(self.text) if w.strip(string.punctuation)
        ]
        self.paragraphs = [p.strip() for p in self.text.split("\n\n") if p.strip()]

    def from_text(self, text):
        """Analyze raw text pasted by the user (no file involved)."""
        self.text = text.strip()
        self._tokenize()
        return self

    def load_text(self):
        from src.readers import read_text_file

        parts = []
        for path in self.filepaths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{path} does not exist")
            parts.append(read_text_file(path))
        self.text = " ".join(parts).strip()
        self._tokenize()
        return self

    # ---------- basic counts ----------
    def word_count(self):
        return len(self.words)

    def sentence_count(self):
        return len(self.sentences)

    def character_count(self):
        return len(self.text)

    def character_count_no_spaces(self):
        return len(re.sub(r"\s", "", self.text))

    def paragraph_count(self):
        return len(self.paragraphs)

    def unique_words_count(self):
        return len(set(self.words))

    # ---------- frequency ----------
    def most_common_words(self, n=5, ignore_stopwords=False):
        words = self.words
        if ignore_stopwords:
            words = [w for w in words if w not in STOPWORDS]
        return Counter(words).most_common(n)

    def letter_frequency(self, n=5):
        letters = [c.lower() for c in self.text if c.isalpha()]
        return Counter(letters).most_common(n)

    def word_frequency(self, word):
        return Counter(self.words)[word.lower()]

    # ---------- readability ----------
    def average_sentence_length(self):
        if not self.sentences:
            return 0
        return sum(len(WORD_RE.findall(s)) for s in self.sentences) / len(self.sentences)

    def longest_sentence(self):
        if not self.sentences:
            return ""
        return max(self.sentences, key=lambda s: len(WORD_RE.findall(s)))

    def shortest_sentence(self):
        if not self.sentences:
            return ""
        return min(self.sentences, key=lambda s: len(WORD_RE.findall(s)))

    def syllable_count(self):
        return sum(count_syllables(w) for w in self.words)

    def flesch_reading_ease(self):
        words = self.word_count()
        if not words or not self.sentences:
            return 0.0
        return round(
            206.835
            - 1.015 * (words / len(self.sentences))
            - 84.6 * (self.syllable_count() / words),
            2,
        )

    def flesch_kincaid_grade(self):
        words = self.word_count()
        if not words or not self.sentences:
            return 0.0
        return round(
            0.39 * (words / len(self.sentences))
            + 11.8 * (self.syllable_count() / words)
            - 15.59,
            2,
        )

    def grade_level_label(self):
        score = self.flesch_reading_ease()
        if score >= 80:
            return "Easy (elementary school)"
        if score >= 60:
            return "Standard (middle school / general audience)"
        if score >= 40:
            return "Fairly difficult (high school)"
        return "Complex (college level)"

    def vocabulary_richness(self):
        if not self.words:
            return 0.0
        return round(self.unique_words_count() / len(self.words), 3)

    def reading_time_minutes(self, wpm=200):
        if not self.words:
            return 0
        return max(1, round(self.word_count() / wpm))

    # ---------- sentiment ----------
    def sentiment(self):
        from src.sentiment import LEXICON

        score = sum(LEXICON.get(w, 0) for w in self.words)
        if score > 0:
            label = "positive"
        elif score < 0:
            label = "negative"
        else:
            label = "neutral"
        return {"score": score, "label": label}

    def keywords(self, n=10):
        """Frequency-weighted keywords with simple tf ranking (no deps)."""
        filtered = [w for w in self.words if w not in STOPWORDS and len(w) > 2]
        total = len(filtered) or 1
        return [
            {"word": w, "count": c, "weight": round(c / total, 4)}
            for w, c in Counter(filtered).most_common(n)
        ]

    # ---------- export ----------
    def metrics(self):
        return {
            "Characters": self.character_count(),
            "CharactersNoSpaces": self.character_count_no_spaces(),
            "Words": self.word_count(),
            "UniqueWords": self.unique_words_count(),
            "Sentences": self.sentence_count(),
            "Paragraphs": self.paragraph_count(),
            "AvgSentenceLength": round(self.average_sentence_length(), 2),
            "Syllables": self.syllable_count(),
            "FleschReadingEase": self.flesch_reading_ease(),
            "FleschKincaidGrade": self.flesch_kincaid_grade(),
            "VocabularyRichness": self.vocabulary_richness(),
            "ReadingTimeMinutes": self.reading_time_minutes(),
            "SentimentScore": self.sentiment()["score"],
        }

    def save_to_csv(self, output_file="analysis.csv"):
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for key, value in self.metrics().items():
                writer.writerow([key, value])
        return output_file

    def save_to_json(self, output_file="analysis.json"):
        data = {
            "metrics": self.metrics(),
            "gradeLevel": self.grade_level_label(),
            "longestSentence": self.longest_sentence(),
            "shortestSentence": self.shortest_sentence(),
            "mostCommonWords": self.most_common_words(10, ignore_stopwords=True),
            "sentiment": self.sentiment(),
            "keywords": self.keywords(),
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return output_file

    def analyze(self):
        """Perform full analysis and print results."""
        self.load_text()
        for key, value in self.metrics().items():
            print(f"{key}: {value}")
        print(f"Grade Level: {self.grade_level_label()}")
        print("Most common words (no stopwords):", self.most_common_words(5, True))
        print("Most common letters:", self.letter_frequency())
        print(f"Longest sentence ({len(WORD_RE.findall(self.longest_sentence()))} words): "
              f"{self.longest_sentence()}")
        print(f"Shortest sentence ({len(WORD_RE.findall(self.shortest_sentence()))} words): "
              f"{self.shortest_sentence()}")
        print("Sentiment:", self.sentiment()["label"], f"({self.sentiment()['score']})")
