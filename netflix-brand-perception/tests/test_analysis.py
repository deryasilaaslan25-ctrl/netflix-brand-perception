import pandas as pd
import pytest

from src.analysis import GENERAL, clean, enrich, find_category, sentiment_label, top_words


def test_word_boundary_fixes_false_positives():
    assert find_category("so happy, loved it") == GENERAL           # "app" ≠ "happy"
    assert find_category("fast downloads") == GENERAL               # "ad" ≠ "downloads"


def test_categories():
    assert find_category("The app keeps crashing") == "Teknik ve Kullanıcı Deneyimi"
    assert find_category("too expensive for the price") == "Fiyat ve Ücretlendirme"
    assert find_category("great series, new season") == "İçerik Kalitesi"
    assert find_category(None) == GENERAL


def test_sentiment_labels():
    assert sentiment_label(0.5) == "Pozitif"
    assert sentiment_label(-0.5) == "Negatif"
    assert sentiment_label(0.0) == "Nötr"


def test_clean_validates_and_drops_bad_rows():
    with pytest.raises(ValueError):
        clean(pd.DataFrame({"foo": [1]}))
    df = pd.DataFrame({"content": ["ok", None, "  "], "score": [5, 3, 1],
                       "at": ["2024-01-01", "2024-01-02", "bad-date"]})
    assert len(clean(df)) == 1


def test_enrich_and_top_words():
    df = pd.DataFrame({"content": ["I love this amazing show", "terrible app, keeps crashing"],
                       "score": [5, 1], "at": ["2024-01-01", "2024-02-01"]})
    out = enrich(df)
    assert list(out["duygu_sinifi"]) == ["Pozitif", "Negatif"]
    assert "crashing" in set(top_words(out["content"])["kelime"])
