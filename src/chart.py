# src/chart.py
"""Word frequency bar chart as a standalone SVG file (no dependencies)."""

import html


def save_word_chart(analyzer, output_file="word_chart.svg", n=10):
    data = analyzer.most_common_words(n, ignore_stopwords=True)
    if not data:
        raise ValueError("No words to chart.")
    bar_w, gap, top_pad, bottom_pad = 60, 20, 60, 60
    width = max(480, len(data) * (bar_w + gap))
    height = 320
    chart_h = height - top_pad - bottom_pad
    max_count = max(c for _, c in data)

    bars = []
    for i, (word, count) in enumerate(data):
        h = max(2, round(count / max_count * chart_h))
        x = i * (bar_w + gap) + gap
        y = top_pad + chart_h - h
        bars.append(
            f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" fill="#4f7cff" rx="4"/>'
            f'<text x="{x + bar_w / 2}" y="{y - 8}" text-anchor="middle" '
            f'font-size="13" fill="#333">{count}</text>'
            f'<text x="{x + bar_w / 2}" y="{height - bottom_pad + 20}" '
            f'text-anchor="middle" font-size="12" fill="#333">'
            f'{html.escape(word)}</text>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="white"/>'
        f'<text x="{width / 2}" y="28" text-anchor="middle" font-size="16" '
        f'font-weight="bold" fill="#222">Top {len(data)} words by frequency</text>'
        + "".join(bars) + "</svg>"
    )
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg)
    return output_file
