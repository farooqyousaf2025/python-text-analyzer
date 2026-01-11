import unittest
import os
import pandas as pd
from src.analyzer import TextAnalyzer

class TestTextAnalyzer(unittest.TestCase):
    def setUp(self):
        self.filepath = "data/sample.txt"
        self.analyzer = TextAnalyzer(self.filepath)
        self.analyzer.load_text()

    # --------- Existing Tests ---------
    def test_word_count(self):
        # Update the expected value to match your sample.txt
        self.assertEqual(self.analyzer.word_count(), 23)

    def test_sentence_count(self):
        self.assertEqual(self.analyzer.sentence_count(), 4)

    def test_character_count(self):
        self.assertGreater(self.analyzer.character_count(), 50)

    # --------- New Feature Tests ---------
    def test_average_sentence_length(self):
        avg_len = self.analyzer.average_sentence_length()
        self.assertTrue(avg_len > 0)
        self.assertAlmostEqual(avg_len, 5.75, places=1)  # Adjust if sample.txt changes

    def test_letter_frequency(self):
        letters = self.analyzer.letter_frequency(n=3)
        self.assertIsInstance(letters, list)
        self.assertEqual(len(letters), 3)
        for letter, count in letters:
            self.assertTrue(letter.isalpha())
            self.assertTrue(count > 0)

    def test_save_to_csv(self):
        output_file = "data/test_analysis.csv"
        # Remove file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        self.analyzer.save_to_csv(output_file)
        # Check if CSV was created
        self.assertTrue(os.path.exists(output_file))
        # Verify contents
        df = pd.read_csv(output_file)
        self.assertIn("Metric", df.columns)
        self.assertIn("Count", df.columns)
        self.assertEqual(len(df), 4)
        os.remove(output_file)  # Clean up

if __name__ == "__main__":
    unittest.main()
