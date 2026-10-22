# src/compare.py
"""Compare two text files side by side."""

from src.analyzer import TextAnalyzer


def compare(file1, file2):
    a = TextAnalyzer(file1).load_text()
    b = TextAnalyzer(file2).load_text()
    set_a, set_b = set(a.words), set(b.words)
    shared = set_a & set_b
    union = set_a | set_b
    rows = [
        ("Words", a.word_count(), b.word_count()),
        ("Sentences", a.sentence_count(), b.sentence_count()),
        ("Characters", a.character_count(), b.character_count()),
        ("Unique words", a.unique_words_count(), b.unique_words_count()),
        ("Avg sentence length", round(a.average_sentence_length(), 2),
         round(b.average_sentence_length(), 2)),
        ("Vocabulary richness", a.vocabulary_richness(), b.vocabulary_richness()),
        ("Flesch reading ease", a.flesch_reading_ease(), b.flesch_reading_ease()),
        ("Sentiment", a.sentiment()["label"], b.sentiment()["label"]),
    ]
    print(f"{'Metric':<22} {file1:>20} {file2:>20}")
    for metric, va, vb in rows:
        print(f"{metric:<22} {str(va):>20} {str(vb):>20}")
    print(f"\nShared words: {len(shared)} "
          f"(Jaccard similarity: {round(len(shared) / len(union), 3) if union else 0})")
    print("Shared words:", sorted(shared) or "none")
    return {"file1": file1, "file2": file2, "sharedWords": len(shared)}
