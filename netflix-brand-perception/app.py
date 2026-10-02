"""Netflix AI Brand Perception Analyzer — Streamlit paneli.

Çalıştırma:  streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import GENERAL, enrich, read_csv, top_words

ROOT = Path(__file__).parent
RED, GREEN, GREY = "#E50914", "#2ECC71", "#8A8A93"
SENT_COLORS = {"Pozitif": GREEN, "Nötr": GREY, "Negatif": RED}
SENT_ORDER = ["Pozitif", "Nötr", "Negatif"]

st.set_page_config(page_title="Netflix Brand Perception Analyzer", page_icon="🎬", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1280px;}
.hero {background: linear-gradient(120deg,#E50914 0%,#7a0510 45%,#16161D 100%);
       padding: 2rem 2.2rem; border-radius: 18px; margin-bottom: 1.2rem;}
.hero h1 {margin:0; font-size: 2.1rem; color:#fff;}
.hero p {margin:.4rem 0 0; color:#ffd9dc; font-size:1.02rem;}
.kpi {background:#16161D; border:1px solid #2a2a33; border-radius:14px; padding:1rem 1.2rem;}
.kpi .l {color:#8A8A93; font-size:.8rem; text-transform:uppercase; letter-spacing:.06em;}
.kpi .v {font-size:1.9rem; font-weight:700; color:#fff; line-height:1.3;}
.card {background:#16161D; border:1px solid #2a2a33; border-left:4px solid #E50914;
       border-radius:12px; padding:1rem 1.2rem; margin-bottom:.8rem;}
.card h4 {margin:0 0 .4rem; color:#fff;}
.card p, .card li {color:#d6d6dc; margin:0;}
footer, #MainMenu {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


def style(fig, height=380):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=height, margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return fig


def kpi(col, label, value):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div></div>',
                 unsafe_allow_html=True)


@st.cache_data(show_spinner="Duygu analizi yapılıyor… (büyük veri setlerinde birkaç dakika sürebilir)")
def analyze(raw: pd.DataFrame) -> pd.DataFrame:
    return enrich(raw)


@st.cache_data(show_spinner=False)
def load_path(path: str) -> pd.DataFrame:
    return read_csv(path)


# ───────────────────────── Sidebar: veri kaynağı ─────────────────────────
st.sidebar.title("🎬 Veri Kaynağı")
uploaded = st.sidebar.file_uploader("Kendi CSV dosyanı yükle", type="csv",
                                    help="Gerekli sütunlar: content, score, at")
real = next((p for p in (ROOT / "netflix_reviews.csv", ROOT / "data" / "netflix_reviews.csv") if p.exists()), None)

try:
    if uploaded is not None:
        raw, source = read_csv(uploaded), f"Yüklenen dosya: {uploaded.name}"
    elif real is not None:
        raw, source = load_path(str(real)), "Gerçek veri: netflix_reviews.csv"
    else:
        raw, source = load_path(str(ROOT / "data" / "sample_reviews.csv")), "Demo (sentetik) veri"
    df = analyze(raw)
except (ValueError, FileNotFoundError, pd.errors.ParserError) as exc:
    st.error(f"Veri yüklenemedi: {exc}")
    st.stop()

if df.empty:
    st.warning("Veri setinde analiz edilebilir yorum bulunamadı.")
    st.stop()

st.sidebar.caption(f"Kaynak: **{source}**")
if source.startswith("Demo"):
    st.sidebar.info("Gerçek Kaggle verisini `netflix_reviews.csv` adıyla proje köküne koyun "
                    "veya yukarıdan yükleyin.")

# ───────────────────────── Sidebar: filtreler ─────────────────────────
st.sidebar.divider()
st.sidebar.subheader("Filtreler")
dmin, dmax = df["at"].min().date(), df["at"].max().date()
dates = st.sidebar.date_input("Tarih aralığı", (dmin, dmax), min_value=dmin, max_value=dmax)
d0, d1 = (dates if isinstance(dates, (tuple, list)) and len(dates) == 2 else (dmin, dmax))
scores = st.sidebar.multiselect("Puan", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])
cats = sorted(df["kategori"].unique())
sel_cats = st.sidebar.multiselect("Kategori", cats, default=cats)
include_general = st.sidebar.toggle("'Genel Yorum' dahil et", value=True)

f = df[(df["at"].dt.date >= d0) & (df["at"].dt.date <= d1)
       & df["score"].isin(scores) & df["kategori"].isin(sel_cats)]
if not include_general:
    f = f[f["kategori"] != GENERAL]

# ───────────────────────── Başlık + KPI ─────────────────────────
st.markdown("""<div class="hero"><h1>🎬 Netflix · AI Brand Perception Analyzer</h1>
<p>Kullanıcı yorumlarından marka algısını ölçen duygu analizi ve strateji paneli</p></div>""",
            unsafe_allow_html=True)

if f.empty:
    st.warning("Seçili filtrelerle eşleşen yorum yok. Filtreleri genişletin.")
    st.stop()

neg_share = (f["duygu_sinifi"] == "Negatif").mean() * 100
pos_share = (f["duygu_sinifi"] == "Pozitif").mean() * 100
focus = f[f["kategori"] != GENERAL]
worst = (focus.groupby("kategori")["duygu_sinifi"].apply(lambda s: (s == "Negatif").mean()).idxmax()
         if not focus.empty else "—")
c = st.columns(5)
kpi(c[0], "Toplam yorum", f"{len(f):,}")
kpi(c[1], "Ortalama puan", f"{f['score'].mean():.2f} ★")
kpi(c[2], "Pozitif", f"%{pos_share:.1f}")
kpi(c[3], "Negatif", f"%{neg_share:.1f}")
kpi(c[4], "En sorunlu alan", worst.split(" ")[0])
st.write("")

tabs = st.tabs(["📊 Genel Bakış", "🧩 Kategoriler", "📈 Trend", "🔤 Kelimeler", "🔎 Yorumlar", "🎯 Kampanya"])

with tabs[0]:
    a, b = st.columns(2)
    sc = f["score"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0).reset_index()
    sc.columns = ["Puan", "Yorum"]
    a.plotly_chart(style(px.bar(sc, x="Puan", y="Yorum", title="Puan dağılımı",
                                color_discrete_sequence=[RED])), use_container_width=True)
    sd = f["duygu_sinifi"].value_counts().reindex(SENT_ORDER, fill_value=0).reset_index()
    sd.columns = ["Duygu", "Yorum"]
    b.plotly_chart(style(px.pie(sd, names="Duygu", values="Yorum", hole=.55, title="Duygu dağılımı",
                                color="Duygu", color_discrete_map=SENT_COLORS)), use_container_width=True)
    x = f.groupby(["score", "duygu_sinifi"]).size().reset_index(name="Yorum")
    st.plotly_chart(style(px.bar(x, x="score", y="Yorum", color="duygu_sinifi", barmode="group",
                                 title="Puana göre duygu sınıfı (model tutarlılığı)",
                                 category_orders={"duygu_sinifi": SENT_ORDER},
                                 color_discrete_map=SENT_COLORS, labels={"score": "Puan"})),
                    use_container_width=True)

with tabs[1]:
    k = f.groupby(["kategori", "duygu_sinifi"]).size().reset_index(name="Yorum")
    st.plotly_chart(style(px.bar(k, x="kategori", y="Yorum", color="duygu_sinifi", barmode="group",
                                 title="Marka özelliklerine göre dijital algı",
                                 category_orders={"duygu_sinifi": SENT_ORDER},
                                 color_discrete_map=SENT_COLORS, labels={"kategori": ""}), 420),
                    use_container_width=True)
    t = f.groupby("kategori").agg(Yorum=("score", "size"), Ort_Puan=("score", "mean"),
                                  Negatif_Oran=("duygu_sinifi", lambda s: (s == "Negatif").mean() * 100))
    st.dataframe(t.round(2).rename(columns={"Ort_Puan": "Ort. Puan", "Negatif_Oran": "Negatif %"}),
                 use_container_width=True)

with tabs[2]:
    m = f.groupby("ay").agg(Ort_Puan=("score", "mean"), Yorum=("score", "size"),
                            Negatif=("duygu_sinifi", lambda s: (s == "Negatif").mean() * 100)).reset_index()
    a, b = st.columns(2)
    a.plotly_chart(style(px.line(m, x="ay", y="Ort_Puan", markers=True, title="Aylık ortalama puan",
                                 labels={"ay": "", "Ort_Puan": "Puan"}, color_discrete_sequence=[RED])),
                   use_container_width=True)
    b.plotly_chart(style(px.area(m, x="ay", y="Negatif", title="Aylık negatif yorum oranı (%)",
                                 labels={"ay": "", "Negatif": "%"}, color_discrete_sequence=[RED])),
                   use_container_width=True)
    tc = (f.groupby(["ay", "kategori"]).size().reset_index(name="Yorum"))
    st.plotly_chart(style(px.line(tc, x="ay", y="Yorum", color="kategori", title="Kategori bazlı yorum hacmi",
                                  labels={"ay": ""})), use_container_width=True)

with tabs[3]:
    cA, cB = st.columns([1, 3])
    pick = cA.radio("Duygu sınıfı", SENT_ORDER, index=2)
    n = cA.slider("Kelime sayısı", 5, 40, 20)
    tw = top_words(f.loc[f["duygu_sinifi"] == pick, "content"], n)
    if tw.empty:
        cB.info("Bu seçim için yeterli metin yok.")
    else:
        cB.plotly_chart(style(px.bar(tw.iloc[::-1], x="adet", y="kelime", orientation="h",
                                     title=f"En sık geçen kelimeler — {pick}",
                                     color_discrete_sequence=[SENT_COLORS[pick]],
                                     labels={"adet": "Adet", "kelime": ""}), 560), use_container_width=True)

with tabs[4]:
    q = st.text_input("Yorumlarda ara", placeholder="örn. crash, price, subscription")
    v = f[f["content"].str.contains(q, case=False, regex=False)] if q else f
    st.caption(f"{len(v):,} yorum")
    show = v[["at", "score", "duygu_sinifi", "kategori", "content"]].sort_values("at", ascending=False)
    st.dataframe(show.head(500).rename(columns={"at": "Tarih", "score": "Puan", "duygu_sinifi": "Duygu",
                                                "kategori": "Kategori", "content": "Yorum"}),
                 use_container_width=True, hide_index=True)
    st.download_button("⬇️ Filtrelenmiş veriyi indir (CSV)", show.to_csv(index=False).encode("utf-8"),
                       "filtrelenmis_yorumlar.csv", "text/csv")

with tabs[5]:
    tech = f[f["kategori"].str.startswith("Teknik")]
    tech_neg = (tech["duygu_sinifi"] == "Negatif").mean() * 100 if len(tech) else 0
    st.markdown(f"""
<div class="card"><h4>Kampanya adı: “Sen Yazdın, Biz Kodladık”</h4>
<p><b>Veri içgörüsü:</b> Filtrelenen veride teknik yorumların <b>%{tech_neg:.1f}</b>'i negatif.
En sorunlu alan: <b>{worst}</b>.</p></div>
<div class="card"><h4>İçgörü (Insight)</h4><p>Kullanıcılar orijinal hikayelere hâlâ tutkuyla bağlı; ancak donma,
yavaşlama ve arayüz hataları izleme deneyimini bölüyor.</p></div>
<div class="card"><h4>Ana mesaj</h4><p>“Bizi eleştirdiğiniz her satırı okuduk, en sevdiğiniz hikayeleri kesintisiz
izleyin diye arka plandaki tüm kodları yeniden yazdık.”</p></div>
<div class="card"><h4>Ses tonu</h4><p>Öz eleştiri yapabilen, şeffaf, samimi ve çözüm odaklı.</p></div>
<div class="card"><h4>İletişim aşamaları</h4><ul>
<li><b>1 · Teaser:</b> Billboardlarda gerçek kullanıcı şikayeti — altında tek cevap: “Haklısınız.”</li>
<li><b>2 · Hero content:</b> Dizi karakterleri ekran donunca komik pozisyonlarda asılı kalır; yazılımcılar
sistemi günceller, akıcılık geri döner.</li>
<li><b>3 · Sürdürülebilir iletişim:</b> Bu panel ile teknik şikayetlerin düşüşü anlık izlenir ve başarı ölçülür.</li>
</ul></div>""", unsafe_allow_html=True)
