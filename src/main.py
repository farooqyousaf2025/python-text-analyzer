# src/main.py

import argparse
from src.analyzer import TextAnalyzer
import os

def main():
    parser = argparse.ArgumentParser(
        description="Python Text Analyzer: Analyze text files for word, sentence, character counts, and more."
    )
    parser.add_argument(
        "file", help="Path to the text file to analyze", type=str
    )
    parser.add_argument(
        "--csv", "-c",
        help="Optional: Save analysis to a CSV file (provide path, e.g., data/analysis.csv)",
        type=str,
        default=None
    )
    args = parser.parse_args()
    file_path = args.file

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    # Initialize analyzer
    analyzer = TextAnalyzer(file_path)
    analyzer.analyze()  # Prints analysis to console

    # Save to CSV if path provided
    if args.csv:
        analyzer.save_to_csv(args.csv)
        print(f"Analysis saved to {args.csv}")

if __name__ == "__main__":
    main()
