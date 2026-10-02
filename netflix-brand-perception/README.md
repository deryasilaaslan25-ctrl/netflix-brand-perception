# 🎬 Netflix · AI Brand Perception Analyzer

Netflix kullanıcı yorumlarını **duygu analizi (NLP)** ile işleyen, marka algısını kategori ve zaman bazında ölçen ve sonuçları bir **iletişim kampanyası stratejisine** dönüştüren etkileşimli veri paneli.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-charts-3F4F75?logo=plotly&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-TextBlob-E50914)

---

 Özellikler

- **KPI kartları:** toplam yorum, ortalama puan, pozitif/negatif oranı, en sorunlu alan
- **Duygu analizi:** her yorum için polarite skoru → *Pozitif / Nötr / Negatif*
- **Marka özelliği kategorileri:** Fiyat ve Ücretlendirme · İçerik Kalitesi · Teknik ve Kullanıcı Deneyimi
- **Zaman trendi:** aylık ortalama puan, negatif oran ve kategori bazlı hacim
- **Kelime analizi:** duygu sınıfına göre en sık geçen kelimeler
- **Yorum gezgini:** arama + filtrelenmiş veriyi CSV olarak indirme
- **Kampanya künyesi:** *“Sen Yazdın, Biz Kodladık”* stratejisi, veriden otomatik hesaplanan içgörüyle
- **Esnek veri kaynağı:** gerçek Kaggle verisi, kendi CSV'niz veya hazır demo veri
- Tarih / puan / kategori filtreleri, hata yönetimi ve önbellekleme

Kurulum

```bash
git clone https://github.com/<kullanici-adin>/netflix-brand-perception.git
cd netflix-brand-perception

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

Tarayıcıda `http://localhost:8501` adresi açılır.

Veri seti

Repoda, panelin hemen çalışması için **sentetik** bir demo veri (`data/sample_reviews.csv`) bulunur.
Gerçek analiz için:

1. [Netflix Reviews (Google Play Store)](https://www.kaggle.com/datasets/ashishkumarak/netflix-reviews-playstore-daily-updated) veri setini Kaggle'dan indirin.
2. `netflix_reviews.csv` dosyasını proje köküne koyun **veya** panelde sol menüden yükleyin.

Gerekli sütunlar: `content` (yorum metni), `score` (1–5 puan), `at` (tarih).
> İlk analizde TextBlob ~110 bin yorumu işler; birkaç dakika sürebilir, sonuç önbelleğe alınır.

Proje yapısı

```
├── app.py                    # Streamlit arayüzü
├── src/analysis.py           # Temizleme, duygu analizi, kategorilendirme
├── generate_sample_data.py   # Demo veri üreticisi
├── data/sample_reviews.csv   # Sentetik demo veri
├── notebooks/                # Keşifsel analiz + LDA konu modelleme
├── tests/                    # pytest (birim + arayüz duman testi)
├── .streamlit/config.toml    # Tema
└── requirements.txt
```

Metodoloji

| Adım | Yöntem |
|------|--------|
| Temizleme | Eksik/bozuk satırlar atılır, tarih ve puan tipleri doğrulanır |
| Duygu | TextBlob polarity; `> 0.1` Pozitif, `< -0.1` Negatif, arası Nötr |
| Kategori | Kelime-sınırlı (regex) anahtar kelime eşleşmesi; en çok eşleşen kategori seçilir |
| Konu modelleme | Notebook'ta gensim LDA + pyLDAvis (negatif yorumlar) |

Orijinal sürüme göre düzeltmeler

- Eksik `netflix_reviews.csv` yüzünden oluşan çökme → demo veri, yükleme alanı ve anlaşılır hata mesajları
- `"ads"`→`"downloads"`, `"app"`→`"happy"` gibi **yanlış kategori eşleşmeleri** → kelime sınırlı regex
- Pandas `SettingWithCopyWarning` → açık `.copy()` / `.loc`
- Sadece `plt.show()` ile çalışan statik grafikler → etkileşimli Plotly grafikleri
- Notebook'taki Kaggle'a sabitlenmiş yol ve kullanılmayan fonksiyon temizlendi
- `requirements.txt` satır sonu (CRLF) ve eksik bağımlılıklar düzeltildi
- Birim ve arayüz testleri eklendi

Test

```bash
pip install -r requirements-dev.txt
pytest
```

Sınırlamalar

- TextBlob **İngilizce** için tasarlanmıştır; ironi ve olumsuzlamayı her zaman yakalayamaz.
- Kategoriler sözlük tabanlıdır; bir yorum tek kategoriye atanır.
- Demo veri sentetiktir, gerçek kullanıcı görüşlerini temsil etmez.

Yol haritası

- [ ] Transformer tabanlı (ör. çok dilli BERT) duygu modeli
- [ ] Panelde LDA konu görselleştirmesi
- [ ] Streamlit Community Cloud'a canlı yayın

Kaynaklar

- Veri: Kaggle · *Netflix Reviews (Playstore, daily updated)*
- Notebook, [Zul](https://www.kaggle.com/zulqarnainalipk)'un Kaggle çalışmasından uyarlanmıştır.
- Netflix adı ve logosu ilgili sahibine aittir; bu proje **eğitim/portföy** amaçlıdır ve Netflix ile bağlantısı yoktur.
Sistem Görselleri
<img width="1364" height="636" alt="Ekran görüntüsü 2026-10-02 173945" src="https://github.com/user-attachments/assets/347fee19-6909-4cd1-afca-976619a506ac" />
<img width="1363" height="635" alt="Ekran görüntüsü 2026-10-02 174115" src="https://github.com/user-attachments/assets/757edb54-8067-414b-9c75-ee2c580f4cd9" />
<img width="1365" height="636" alt="Ekran görüntüsü 2026-10-02 174323" src="https://github.com/user-attachments/assets/1c029c99-503a-439b-832b-6307c79c3c24" />
<img width="1365" height="636" alt="Ekran görüntüsü 2026-10-02 174351" src="https://github.com/user-attachments/assets/7a76e568-3f84-4036-ac64-8678a3ce6ec6" />
<img width="1364" height="646" alt="Ekran görüntüsü 2026-10-02 174428" src="https://github.com/user-attachments/assets/6fd75cef-6fe9-4c27-a8a1-1cda7792cff7" />
