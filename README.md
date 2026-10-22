# Python Text Analyzer

A Python project to analyze text files: counts, readability, sentiment, keywords, and charts.
Fully tested, modular, zero third-party dependencies — perfect for portfolios and GitHub showcase.

## Features

**Counts**
- Words, sentences (splits on `.`, `!`, `?`), characters (with/without spaces), paragraphs
- Unique word count and vocabulary richness score
- Most common words (optionally with stopwords filtered) and most common letters

**Readability**
- Average sentence length, longest/shortest sentence
- Syllable count, Flesch Reading Ease, Flesch-Kincaid grade level
- Reading time estimate

**Analysis**
- Sentiment label (positive / neutral / negative) using a built-in lexicon
- Keyword extraction with frequency weights
- Compare two files side by side (Jaccard word similarity, metric table)
- Find a word: occurrence count + every sentence containing it

**Input formats**
- Plain text (.txt), Markdown (.md), Word (.docx) and PDF (.pdf) files
- DOCX uses stdlib zip/XML parsing; PDF uses a built-in extractor, or `pypdf` automatically if you have it installed

**Export**
- CSV metrics export (`--csv`)
- Full JSON report (`--json`)
- Word-frequency bar chart as SVG (`--chart`)

**Interface**
- Easy-to-use command-line interface, one or many files at once
- Local web UI — paste text or drag in a file in your browser (`--web`)
- Analysis history dashboard backed by SQLite (`--history`)
- Installable as a command-line tool via pip (`text-analyzer` command)
- 22 unit tests included for reliability

## Folder Structure

```
python-text-analyzer/
├── src/
│   ├── analyzer.py     # TextAnalyzer core class
│   ├── main.py         # CLI entry point
│   ├── readers.py      # .txt / .md / .docx / .pdf input
│   ├── compare.py      # two-file comparison
│   ├── chart.py        # SVG word-frequency chart
│   ├── history.py      # SQLite analysis log
│   ├── web.py          # local web UI (stdlib http.server)
│   ├── stopwords.py    # English stopword list
│   └── sentiment.py    # positive/negative lexicon
├── tests/              # 22 unit tests
├── data/               # sample .txt/.docx/.pdf files
├── pyproject.toml      # pip packaging (text-analyzer command)
├── requirements.txt
└── README.md
```

## Installation

Python 3.10+ is the only requirement — no packages to install to run the tool.

```
git clone git@github.com:farooqyousaf2025/python-text-analyzer.git
cd python-text-analyzer
python -m venv .venv
.venv\Scripts\activate        # Windows  (source .venv/bin/activate on Linux/Mac)
```

Optional — install as a global command:

```
pip install -e .
text-analyzer data/sample.txt
```

## Usage

Run from the project root (or use the `text-analyzer` command after pip install):

```
python -m src.main data/sample.txt
python -m src.main data/sample.txt data/sample2.txt              # multiple files combined
python -m src.main report.docx                                   # .docx / .pdf / .md work too
python -m src.main data/sample.txt --csv out.csv --json out.json --chart chart.svg
python -m src.main data/sample.txt --find python                 # count + context sentences
python -m src.main data/sample.txt --keywords 10                 # top keywords
python -m src.main --compare data/sample.txt data/sample2.txt    # side-by-side comparison
python -m src.main --history                                     # last 20 logged analyses
python -m src.main --history-clear                               # wipe history
python -m src.main --web --web-open                              # browser UI at http://127.0.0.1:8000
```

Example output:

```
Characters: 136
Words: 23
Sentences: 4
AvgSentenceLength: 5.75
Syllables: 37
FleschReadingEase: 64.9
VocabularyRichness: 0.913
ReadingTimeMinutes: 1
SentimentScore: 4
Most common words (no stopwords): [('python', 2), ('analysis', 2), ...]
```

## Testing

```
python -m unittest discover -s tests
```

## Example Code

```python
from src.analyzer import TextAnalyzer

analyzer = TextAnalyzer("data/sample.txt").load_text()
analyzer.analyze()
analyzer.save_to_csv("data/analysis.csv")
analyzer.save_to_json("data/analysis.json")
```

## Dependencies

- Python 3.10+ (standard library only)

## Author

Farooq Yousaf

Email: farooqyousaf2025@gmail.com

GitHub: https://github.com/farooqyousaf2025

## License

MIT License
