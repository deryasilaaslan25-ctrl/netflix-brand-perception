"""Demo için SENTETİK yorum verisi üretir (gerçek kullanıcı verisi içermez)."""
import random
from pathlib import Path

import pandas as pd

random.seed(42)
POS = {
    "tech": ["The app is smooth and fast, no crashes at all", "Great interface, loading is quick and easy"],
    "price": ["Worth every penny, the subscription price is fair", "Good value for the money"],
    "content": ["Amazing series, I love every episode", "Best shows and movies, the new season is wonderful"],
    "gen": ["Love it, highly recommend", "Excellent, five stars"],
}
NEG = {
    "tech": ["The app keeps freezing and crashing after the update", "Terrible bug, screen is stuck on loading",
             "Very slow and buggy interface, constant error on login"],
    "price": ["Too expensive, the price keeps going up", "Ads and a higher subscription cost, waste of money",
              "Payment failed again and no refund"],
    "content": ["Boring shows, they cancelled my favorite series", "Bad movies lately, the new season is awful"],
    "gen": ["Worst experience ever", "Very disappointed, I hate it"],
}
NEU = ["It is okay", "Works as expected", "Average, nothing special", "Fine for now"]


def make_row(day: pd.Timestamp) -> dict:
    # Zamanla teknik şikayetler azalır (kampanya sonrası iyileşme senaryosu)
    progress = (day - pd.Timestamp("2023-01-01")).days / 530
    p_neg = 0.42 - 0.15 * progress
    topic = random.choices(["tech", "price", "content", "gen"], weights=[3 - 1.5 * progress, 2, 3, 1])[0]
    r = random.random()
    if r < p_neg:
        text, score = random.choice(NEG[topic]), random.choice([1, 1, 2, 2, 3])
    elif r < p_neg + 0.12:
        text, score = random.choice(NEU), 3
    else:
        text, score = random.choice(POS[topic]), random.choice([4, 5, 5])
    return {"content": text, "score": score,
            "at": (day + pd.Timedelta(seconds=random.randint(0, 86399))).strftime("%Y-%m-%d %H:%M:%S")}


days = pd.date_range("2023-01-01", "2024-06-14")
rows = [make_row(random.choice(days)) for _ in range(4000)]
out = Path(__file__).parent / "data" / "sample_reviews.csv"
pd.DataFrame(rows).sort_values("at").to_csv(out, index=False)
print(f"{len(rows)} satır yazıldı -> {out}")
