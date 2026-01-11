Python Text Analyzer

A Python project to analyze text files for word frequency, character count, sentence statistics, and more.
It’s fully tested, modular, and easy to run—perfect for portfolios and GitHub showcase.

Features

Count words, sentences, and characters

Calculate average sentence length

Find most common words and letters

Support multiple text files

Export analysis results to CSV

Easy-to-use command-line interface

Unit tests included for reliability

Folder Structure
python-text-analyzer/
├── src/          # Python source code
│   └── analyzer.py
├── tests/        # Unit tests
│   └── test_analyzer.py
├── data/         # Sample text files
│   └── sample.txt
├── docs/         # Documentation
├── .venv/        # Virtual environment
├── requirements.txt
└── README.md

Installation

Clone the repository:

git clone git@github.com:farooqyousaf2025/python-text-analyzer.git
cd python-text-analyzer


Create a virtual environment:

python -m venv .venv


Activate the virtual environment:

Windows:

.venv\Scripts\activate


Linux/Mac:

source .venv/bin/activate


Install dependencies:

pip install -r requirements.txt

Usage

Place your text file(s) in the data/ folder.

Run the analyzer using Python:

python src/main.py


Example output:

Characters: 132
Words: 23
Sentences: 4
Average Sentence Length: 5.75 words
Most common words: [('python', 3), ('text', 2), ...]
Most common letters: [('t', 12), ('e', 10), ('s', 8)]
Analysis saved to analysis.csv


Results are also saved as analysis.csv in the project root.

Testing

Run unit tests to verify the functionality:

python -m unittest discover -s tests


Tests cover:

Word, sentence, and character counts

Average sentence length

Letter frequency

CSV export

Example Code
from src.analyzer import TextAnalyzer

analyzer = TextAnalyzer("data/sample.txt")
analyzer.analyze()  # Run analysis and print results
analyzer.save_to_csv("data/analysis.csv")  # Optional: save results

Dependencies

Python 3.10+

pandas (for CSV export)

Install dependencies with:

pip install pandas

Author

Farooq Yousaf

Email: farooqyousaf2025@gmail.com

GitHub: https://github.com/farooqyousaf2025

License

MIT License