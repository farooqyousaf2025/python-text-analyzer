import os
import unittest

from src.analyzer import TextAnalyzer
from src.history import clear, list_analyses, log_analysis
from src.readers import read_docx, read_pdf_basic, read_text_file

DOCX = "data/sample.docx"
PDF = "data/sample.pdf"


@unittest.skipUnless(os.path.exists(DOCX), "docx fixture missing")
class TestDocxReader(unittest.TestCase):
    def test_read_docx(self):
        text = read_docx(DOCX)
        self.assertIn("The cat sat on the windowsill.", text)

    def test_analyzer_accepts_docx(self):
        a = TextAnalyzer(DOCX).load_text()
        self.assertEqual(a.word_count(), 18)
        self.assertEqual(a.sentence_count(), 3)


@unittest.skipUnless(os.path.exists(PDF), "pdf fixture missing")
class TestPdfReader(unittest.TestCase):
    def test_read_pdf_basic(self):
        text = read_pdf_basic(PDF)
        self.assertIn("She watched the rain fall.", text)

    def test_analyzer_accepts_pdf(self):
        a = TextAnalyzer(PDF).load_text()
        self.assertEqual(a.word_count(), 18)
        self.assertEqual(a.sentence_count(), 3)


class TestFromText(unittest.TestCase):
    def test_from_text(self):
        a = TextAnalyzer(["pasted"]).from_text("Hello there! How are you? Fine.")
        self.assertEqual(a.word_count(), 6)
        self.assertEqual(a.sentence_count(), 3)


class TestHistory(unittest.TestCase):
    DB = "data/test_history.db"

    def tearDown(self):
        if os.path.exists(self.DB):
            os.remove(self.DB)

    def test_log_list_clear(self):
        a = TextAnalyzer("data/sample.txt").load_text()
        log_analysis(a, db_path=self.DB, source="unit test")
        log_analysis(a, db_path=self.DB, source="unit test 2")
        rows = list_analyses(db_path=self.DB)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][2], "unit test 2")  # newest first
        self.assertEqual(rows[0][3], 23)  # word count
        clear(db_path=self.DB)
        self.assertEqual(list_analyses(db_path=self.DB), [])


if __name__ == "__main__":
    unittest.main()
