"""Netflix yorumları için veri temizleme, duygu analizi ve kategorilendirme."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import IO, Union

import pandas as pd
from textblob import TextBlob

REQUIRED_COLUMNS = ("content", "score", "at")
POS_THRESHOLD, NEG_THRESHOLD = 0.1, -0.1

CATEGORIES: dict[str, list[str]] = {
    "Fiyat ve Ücretlendirme": ["price", "expensive", "pay", "payment", "money", "cost",
                               "ad", "ads", "subscription", "charge", "refund", "plan"],
    "İçerik Kalitesi": ["movie", "show", "series", "anime", "drama", "season",
                        "episode", "content", "documentary", "film"],
    "Teknik ve Kullanıcı Deneyimi": ["crash", "bug", "app", "update", "slow", "freeze",
                                     "screen", "interface", "loading", "error", "login", "buffering"],
}
GENERAL = "Genel Yorum"

# Kelime sınırı (\b) kullanılır: "ads" artık "downloads" içinde, "app" artık "happy" içinde eşleşmez.
_PATTERNS = {
    cat: re.compile(r"\b(?:%s)(?:s|es|ed|ing)?\b" % "|".join(map(re.escape, words)))
    for cat, words in CATEGORIES.items()
}

STOPWORDS = set("""a about all also am an and any are as at be because been but by can cant could did do does dont
for from get got had has have he her him his how i if im in is it its ive just like me more my no not now of on one
only or our out so some than that the their them then there they this to too up us very was we were what when which
who will with would you your netflix app movie movies show shows series time phone watch""".split())


def sentiment_score(text: object) -> float:
    """TextBlob polarity (-1..+1). Metin olmayan değerler için 0.0 döner."""
    return TextBlob(text).sentiment.polarity if isinstance(text, str) and text.strip() else 0.0


def sentiment_label(score: float) -> str:
    if score > POS_THRESHOLD:
        return "Pozitif"
    if score < NEG_THRESHOLD:
        return "Negatif"
    return "Nötr"


def find_category(text: object) -> str:
    """En çok anahtar kelime eşleşmesi olan kategoriyi döndürür (eşitlikte sözlük sırası)."""
    if not isinstance(text, str):
        return GENERAL
    low = text.lower()
    hits = {c: len(p.findall(low)) for c, p in _PATTERNS.items()}
    best = max(hits, key=hits.get)
    return best if hits[best] > 0 else GENERAL


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Gerekli sütunları doğrular, tipleri düzeltir, bozuk satırları atar."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV dosyasında gerekli sütunlar eksik: {', '.join(missing)}. "
            f"Beklenen sütunlar: {', '.join(REQUIRED_COLUMNS)}"
        )
    out = df.loc[:, list(REQUIRED_COLUMNS)].copy()
    out["at"] = pd.to_datetime(out["at"], errors="coerce")
    out["score"] = pd.to_numeric(out["score"], errors="coerce")
    out = out.dropna(subset=["content", "score", "at"])
    out = out[out["content"].astype(str).str.strip() != ""]
    out["score"] = out["score"].clip(1, 5).round().astype(int)
    out["content"] = out["content"].astype(str)
    return out.reset_index(drop=True)


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Duygu skoru/sınıfı, kategori ve ay sütunlarını ekler."""
    out = clean(df)
    out["duygu_skoru"] = out["content"].map(sentiment_score)
    out["duygu_sinifi"] = out["duygu_skoru"].map(sentiment_label)
    out["kategori"] = out["content"].map(find_category)
    out["ay"] = out["at"].dt.to_period("M").dt.to_timestamp()
    return out


def read_csv(source: Union[str, Path, IO]) -> pd.DataFrame:
    try:
        return pd.read_csv(source)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("CSV dosyası boş.") from exc


def top_words(texts: pd.Series, n: int = 20) -> pd.DataFrame:
    counter: Counter = Counter()
    for t in texts:
        counter.update(w for w in re.findall(r"[a-z]{3,}", t.lower()) if w not in STOPWORDS)
    return pd.DataFrame(counter.most_common(n), columns=["kelime", "adet"])
