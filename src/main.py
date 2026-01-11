# src/main.py

from analyzer import TextAnalyzer

def main():
    filepath = input("Enter text file path (e.g., data/sample.txt): ")
    analyzer = TextAnalyzer(filepath)
    try:
        analyzer.analyze()
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
