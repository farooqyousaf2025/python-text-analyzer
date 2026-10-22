import csv
import json
import os
import unittest

from src.analyzer import TextAnalyzer, count_syllables
from src.compare import compare
from src.chart import save_word_chart


class TestTextAnalyzer(unittest.TestCase):
    def setUp(self):
        self.filepath = "data/sample.txt"
        self.analyzer = TextAnalyzer(self.filepath).load_text()

    # --------- basic counts ---------
    def test_word_count(self):
        self.assertEqual(self.analyzer.word_count(), 23)

    def test_sentence_count(self):
        self.assertEqual(self.analyzer.sentence_count(), 4)

    def test_character_count(self):
        self.assertGreater(self.analyzer.character_count(), 50)

    def test_average_sentence_length(self):
        self.assertAlmostEqual(self.analyzer.average_sentence_length(), 5.75, places=1)

    def test_letter_frequency(self):
        letters = self.analyzer.letter_frequency(n=3)
        self.assertEqual(len(letters), 3)
        for letter, count in letters:
            self.assertTrue(letter.isalpha())
            self.assertTrue(count > 0)

    # --------- sentence splitting fixes ---------
    def test_sentence_split_on_exclamation_and_question(self):
        with open("data/tmp_test.txt", "w", encoding="utf-8") as f:
            f.write("Hello there! How are you? I am fine.")
        try:
            a = TextAnalyzer("data/tmp_test.txt").load_text()
            self.assertEqual(a.sentence_count(), 3)
        finally:
            os.remove("data/tmp_test.txt")

    def test_no_empty_word_tokens(self):
        with open("data/tmp_test.txt", "w", encoding="utf-8") as f:
            f.write("One two three. ! ? ...")
        try:
            a = TextAnalyzer("data/tmp_test.txt").load_text()
            self.assertTrue(all(w for w in a.words))
            self.assertEqual(a.word_count(), 3)
        finally:
            os.remove("data/tmp_test.txt")

    # --------- new metrics ---------
    def test_multi_file_load(self):
        a = TextAnalyzer(["data/sample.txt", "data/sample2.txt"]).load_text()
        single = TextAnalyzer("data/sample.txt").load_text()
        self.assertGreater(a.word_count(), single.word_count())

    def test_syllable_counter(self):
        self.assertEqual(count_syllables("dog"), 1)
        self.assertEqual(count_syllables("beautiful"), 3)
        self.assertGreaterEqual(count_syllables("python"), 2)

    def test_reading_time_and_richness(self):
        self.assertGreaterEqual(self.analyzer.reading_time_minutes(), 1)
        self.assertTrue(0 < self.analyzer.vocabulary_richness() <= 1)

    def test_sentiment(self):
        with open("data/tmp_test.txt", "w", encoding="utf-8") as f:
            f.write("This is great and wonderful!")
        try:
            a = TextAnalyzer("data/tmp_test.txt").load_text()
            self.assertEqual(a.sentiment()["label"], "positive")
        finally:
            os.remove("data/tmp_test.txt")

    def test_keywords_exclude_stopwords(self):
        kws = [k["word"] for k in self.analyzer.keywords()]
        self.assertNotIn("the", kws)

    # --------- exports ---------
    def test_save_to_csv(self):
        output_file = "data/test_analysis.csv"
        self.analyzer.save_to_csv(output_file)
        try:
            with open(output_file, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            self.assertEqual(rows[0], ["Metric", "Value"])
            self.assertGreater(len(rows), 4)
        finally:
            os.remove(output_file)

    def test_save_to_json(self):
        output_file = "data/test_analysis.json"
        self.analyzer.save_to_json(output_file)
        try:
            with open(output_file, encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("metrics", data)
            self.assertIn("keywords", data)
            self.assertIn("Words", data["metrics"])
        finally:
            os.remove(output_file)

    def test_word_chart(self):
        output_file = "data/test_chart.svg"
        save_word_chart(self.analyzer, output_file)
        try:
            with open(output_file, encoding="utf-8") as f:
                svg = f.read()
            self.assertTrue(svg.startswith("<svg"))
            self.assertIn("<rect", svg)
        finally:
            os.remove(output_file)

    def test_compare(self):
        result = compare("data/sample.txt", "data/sample2.txt")
        self.assertEqual(result["file1"], "data/sample.txt")


if __name__ == "__main__":
    unittest.main()
