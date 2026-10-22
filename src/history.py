# src/history.py
"""SQLite log of past analyses (stdlib only)."""

import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join("data", "history.db")


def _connect(db_path):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    return sqlite3.connect(db_path)


def log_analysis(analyzer, db_path=DB_PATH, source=None):
    conn = _connect(db_path)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                words INTEGER,
                sentences INTEGER,
                characters INTEGER,
                avg_sentence_length REAL,
                flesch_reading_ease REAL,
                sentiment TEXT,
                metrics_json TEXT
            )"""
        )
        m = analyzer.metrics()
        conn.execute(
            """INSERT INTO analyses (timestamp, source, words, sentences, characters,
               avg_sentence_length, flesch_reading_ease, sentiment, metrics_json)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                source or ", ".join(analyzer.filepaths),
                m["Words"], m["Sentences"], m["Characters"],
                m["AvgSentenceLength"], m["FleschReadingEase"],
                m["SentimentScore"], json.dumps(m),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def list_analyses(limit=20, db_path=DB_PATH):
    if not os.path.exists(db_path):
        return []
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """SELECT id, timestamp, source, words, sentences, characters,
               avg_sentence_length, flesch_reading_ease, sentiment
               FROM analyses ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    finally:
        conn.close()
    return rows


def clear(db_path=DB_PATH):
    if os.path.exists(db_path):
        os.remove(db_path)
        return 1
    return 0
