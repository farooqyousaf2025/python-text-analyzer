import unittest
from src.analyzer import TextAnalyzer

class TestTextAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TextAnalyzer("data/sample.txt")
        self.analyzer.load_text()

    def test_word_count(self):
        self.assertEqual(self.analyzer.word_count(), 18)

    def test_sentence_count(self):
        self.assertEqual(self.analyzer.sentence_count(), 4)

    def test_character_count(self):
        self.assertGreater(self.analyzer.character_count(), 50)

if __name__ == "__main__":
    unittest.main()
