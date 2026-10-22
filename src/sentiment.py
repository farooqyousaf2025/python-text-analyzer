# src/sentiment.py
"""Small positive/negative word lexicon (AFINN-style scores, -2..2)."""

LEXICON = {
    # positive
    "good": 1, "great": 2, "excellent": 2, "amazing": 2, "awesome": 2,
    "happy": 1, "glad": 1, "love": 2, "like": 1, "enjoy": 1, "enjoyed": 1,
    "beautiful": 1, "best": 2, "nice": 1, "wonderful": 2, "fantastic": 2,
    "perfect": 2, "help": 1, "helps": 1, "helped": 1, "learn": 1,
    "quick": 1, "laughed": 1, "played": 1, "sun": 1, "green": 1,
    "success": 2, "win": 2, "winning": 2, "clear": 1, "easy": 1,
    "fast": 1, "friendly": 1, "fun": 1, "smart": 1, "strong": 1,
    "clean": 1, "free": 1, "calm": 1, "quietly": 1, "bright": 1,
    # negative
    "bad": -1, "terrible": -2, "horrible": -2, "awful": -2, "sad": -1,
    "hate": -2, "angry": -1, "ugly": -1, "worst": -2, "poor": -1,
    "fail": -2, "failed": -2, "failure": -2, "error": -1, "broken": -1,
    "slow": -1, "weak": -1, "hard": -1, "difficult": -1, "lost": -1,
    "lazy": -1, "slept": -1, "dark": -1, "cold": -1, "dirty": -1,
    "hurt": -2, "pain": -2, "cry": -1, "crying": -1, "kill": -2,
    "dead": -2, "death": -2, "war": -2, "crime": -2, "danger": -2,
    "wrong": -1, "boring": -1, "tired": -1, "stupid": -2, "mess": -1,
}
