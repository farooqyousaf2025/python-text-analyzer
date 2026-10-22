# src/main.py
"""CLI: analyze one or more text files.

Examples:
    python -m src.main data/sample.txt
    python -m src.main data/sample.txt data/sample2.txt --csv out.csv --json out.json
    python -m src.main data/sample.txt --chart chart.svg --keywords 10
    python -m src.main data/sample.txt --find python
    python -m src.main --compare data/sample.txt data/sample2.txt
"""

import argparse
import os
import sys

from src.analyzer import TextAnalyzer, WORD_RE
from src.chart import save_word_chart
from src.compare import compare
from src.history import clear, list_analyses, log_analysis


def build_parser():
    parser = argparse.ArgumentParser(
        prog="text-analyzer",
        description="Analyze text files: counts, readability, sentiment, keywords, charts, exports.",
    )
    parser.add_argument("files", nargs="*", help="One or more text files to analyze")
    parser.add_argument("--csv", metavar="PATH", help="Save metrics to a CSV file")
    parser.add_argument("--json", metavar="PATH", help="Save full analysis to a JSON file")
    parser.add_argument("--chart", metavar="PATH", help="Save a word-frequency SVG bar chart")
    parser.add_argument("--find", metavar="WORD", help="Count occurrences and show sentences containing WORD")
    parser.add_argument("--min-words", type=int, default=1, metavar="N", help="Warn if the text has fewer than N words")
    parser.add_argument("--keywords", type=int, metavar="N", nargs="?", const=10, help="Print top N keywords (default 10)")
    parser.add_argument("--no-stopwords", action="store_true", help="Hide stopwords in the common-words list")
    parser.add_argument("--compare", nargs=2, metavar=("FILE1", "FILE2"), help="Compare two files side by side")
    parser.add_argument("--history", nargs="?", const=20, type=int, metavar="N", help="Show the last N analyses (default 20)")
    parser.add_argument("--history-clear", action="store_true", help="Delete all history records")
    parser.add_argument("--no-history", action="store_true", help="Do not log this analysis to history")
    parser.add_argument("--web", nargs="?", const=8000, type=int, metavar="PORT", help="Start the web UI (default port 8000)")
    parser.add_argument("--web-open", action="store_true", help="With --web, also open the browser automatically")
    return parser


def run(args):
    if args.web is not None:
        from src.web import serve
        serve(port=args.web, open_browser=args.web_open)
        return 0

    if args.history_clear:
        clear()
        print("History cleared.")
        return 0

    if args.history is not None:
        rows = list_analyses(limit=args.history)
        if not rows:
            print("No analyses logged yet.")
            return 0
        print(f"{'ID':<4}{'Timestamp':<21}{'Words':>7}{'Sent.':>7}{'Chars':>8}{'AvgLen':>8}{'Flesch':>8}{'Sent':>6}  Source")
        for r in rows:
            print(f"{r[0]:<4}{r[1]:<21}{r[3]:>7}{r[4]:>7}{r[5]:>8}{r[6]:>8}{r[7]:>8}{r[8]:>6}  {r[2]}")
        return 0

    if args.compare:
        for path in args.compare:
            if not os.path.exists(path):
                print(f"Error: File '{path}' does not exist.")
                return 1
        compare(*args.compare)
        return 0

    if not args.files:
        print("Error: provide at least one text file (or use --compare FILE1 FILE2).")
        return 1

    missing = [p for p in args.files if not os.path.exists(p)]
    if missing:
        for p in missing:
            print(f"Error: File '{p}' does not exist.")
        return 1

    analyzer = TextAnalyzer(args.files).load_text()

    if args.min_words > 1 and analyzer.word_count() < args.min_words:
        print(f"Warning: only {analyzer.word_count()} words (minimum requested: {args.min_words}).")

    analyzer.analyze()
    if not args.no_history:
        log_analysis(analyzer)
    if args.no_stopwords:
        print("Filtered top words:", analyzer.most_common_words(10, ignore_stopwords=True))

    if args.find:
        word = args.find.lower()
        print(f"\n'{word}' appears {analyzer.word_frequency(word)} time(s).")
        for s in analyzer.sentences:
            if word in s.lower():
                print("  -", s)

    if args.keywords is not None:
        print("\nKeywords:")
        for kw in analyzer.keywords(args.keywords):
            print(f"  {kw['word']:<15} count={kw['count']} weight={kw['weight']}")

    if args.csv:
        print(f"Analysis saved to {analyzer.save_to_csv(args.csv)}")
    if args.json:
        print(f"Analysis saved to {analyzer.save_to_json(args.json)}")
    if args.chart:
        print(f"Chart saved to {save_word_chart(analyzer, args.chart)}")
    return 0


def main():
    sys.exit(run(build_parser().parse_args()))


if __name__ == "__main__":
    main()
