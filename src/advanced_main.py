# src/advanced_main.py

from src.advanced_analyzer import AdvancedTextAnalyzer

analyzer = AdvancedTextAnalyzer(["data/sample.txt", "data/sample2.txt"])
analyzer.analyze()
