from pathlib import Path
import html
import pandas as pd
import plotly.express as px
import streamlit as st
from src.eda import render_eda
from src.advisor import render_advisor
from src.visuals import cinematic_home

st.set_page_config(
    page_title="EstateVision AI",
    page_icon="🏙️",
    layout="wide"
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data/processed/housing_cleaned.csv"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
.stApp {
    background: radial-gradient(ellipse at 85% 0%, #25204b 0%, #101521 42%, #090e17 100%);
    color: #eef2ff;
    font-family: 'DM Sans', sans-serif;
}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif !important;}
.block-container {padding-top:2rem; max-width:1450px;}
[data-testid="stSidebar"] {background:#101724; border-right:1px solid #ffffff12;}
.hero {
    padding:52px 42px;
    border:1px solid #ffffff24;
    border-radius:26px;
    background:linear-gradient(115deg,#172943,#26204a 65%,#49315c);
    position:relative;
    overflow:hidden;
    margin-bottom:24px;
    animation:appear .7s ease-out;
}
.hero:after {
    content:"";
    position:absolute;
    width:260px;height:260px;
    right:-70px;bottom:-160px;
    border:45px solid #7ce7df20;
    border-radius:50%;
    pointer-events:none;
}
.eyebrow {color:#7ce7df;letter-spacing:3px;font-size:12px;font-weight:700;}
.hero h1 {font-size:clamp(36px,5vw,66px);line-height:1.05;max-width:850px;margin:18px 0;}
.hero p {color:#c4cde0;max-width:660px;font-size:17px;line-height:1.7;}
.accent {color:#7ce7df;}
.property {
    background:linear-gradient(140deg,#182638,#171b30);
    border:1px solid #ffffff20;border-radius:18px;
    padding:24px;min-height:240px;margin-bottom:18px;
}
.property h3 {font-size:22px;margin:12px 0;}
.property p {color:#b7c5da;}
.price {font-size:30px;font-weight:700;color:#7ce7df;}
.tag {color:#c7baff;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;}
[data-testid="stMetric"] {
    background:#ffffff07;border:1px solid #ffffff16;
    padding:20px;border-radius:16px;
}
[data-testid="stMetricValue"] {color:#7ce7df;}
@keyframes appear {from {opacity:0;transform:translateY(12px)} to {opacity:1;transform:translateY(0)}}
@media(prefers-reduced-motion:reduce){.hero{animation:none}}
@media(max-width:600px){.hero{padding:28px 22px}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(path, modified):
    return pd.read_csv(path)

def chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce6f5"),
        margin=dict(l=10,r=10,t=40,b=10),
        colorway=["#7ce7df","#ae91ff","#ffb99f","#9bbcff"]
    )
    st.plotly_chart(fig, use_container_width=True)

def money(lakhs):
    return f"₹{lakhs / 100:.2f} Cr" if lakhs >= 100 else f"₹{lakhs:.2f} L"

if not DATA.exists():
    st.error("Cleaned dataset not found. Run: python src/prepare_data.py")
    st.stop()

df = load_data(str(DATA), DATA.stat().st_mtime)

with st.sidebar:
    st.markdown("## 🏙️ EstateVision")
    st.caption("PROPERTY INTELLIGENCE")
    page = st.radio(
        "Explore",
        ["Overview", "Property Explorer", "Investment Advisor", "Market Intelligence", "Growth Simulator", "EDA Lab", "Data Quality"]
    )
    st.divider()
    st.caption("Developed by Aayushi Suryawanshi")
    st.markdown("[View GitHub repository](https://github.com/aayuabcd/estatevision-ai)")
    st.caption("Dataset analysis and illustrative growth scenarios.")

if page == "Overview":
    cinematic_home(df)

    a,b,c,d = st.columns(4)
    a.metric("Properties", f"{len(df):,}")
    b.metric("Cities", df["City"].nunique())
    c.metric("States", df["State"].nunique())
    d.metric("Median asking price", money(df["Price_in_Lakhs"].median()))

    st.write("")
    left,right = st.columns([1.25,1])
    with left:
        st.subheader("Explore the market")
        top = (
            df.groupby("City", as_index=False)["Price_in_Lakhs"]
            .median().nlargest(10, "Price_in_Lakhs")
            .sort_values("Price_in_Lakhs")
        )
        chart(px.bar(
            top, x="Price_in_Lakhs", y="City", orientation="h",
            labels={"Price_in_Lakhs":"Median price (₹ lakhs)"},
            title="Ten cities with the highest median asking prices"
        ))
    with right:
        st.subheader("Built for informed exploration")
        st.markdown("""
**Find your shortlist**  
Filter listings by location, budget, size, and property type.

**Read the market**  
Compare asking prices, amenities, and neighbourhood indicators.

**Explore future scenarios**  
Adjust a growth assumption and see its five-year effect.
""")
        st.info("Open Investment Advisor for trained model screening and evaluation. Growth Simulator uses a transparent compound-growth calculation.")

elif page == "Property Explorer":
    st.title("Find a place. See the possibilities.")
    st.caption("Filter the supplied dataset. Listing details are dataset records, not verified live advertisements.")

    a,b,c = st.columns(3)
    state = a.selectbox("State", ["All"] + sorted(df["State"].dropna().unique().tolist()))
    subset = df if state == "All" else df[df["State"] == state]
    city = b.selectbox("City", ["All"] + sorted(subset["City"].dropna().unique().tolist()))
    if city != "All":
        subset = subset[subset["City"] == city]
    kind = c.selectbox("Property type", ["All"] + sorted(subset["Property_Type"].dropna().unique().tolist()))
    if kind != "All":
        subset = subset[subset["Property_Type"] == kind]

    a,b,c = st.columns(3)
    budget = a.number_input("Maximum budget (₹ lakhs)", min_value=1.0, value=500.0, step=10.0)
    bhk = b.selectbox("BHK", ["Any"] + sorted(df["BHK"].dropna().unique().tolist()))
    min_size = c.number_input("Minimum size (sq ft)", min_value=0, value=0, step=100)

    subset = subset[
        (subset["Price_in_Lakhs"] <= budget)
        & (subset["Size_in_SqFt"] >= min_size)
    ]
    if bhk != "Any":
        subset = subset[subset["BHK"] == bhk]

    sort = st.selectbox("Sort by", ["Lowest price", "Highest price", "Lowest price per sq ft"])
    field = "Price_per_SqFt" if sort == "Lowest price per sq ft" else "Price_in_Lakhs"
    subset = subset.sort_values(field, ascending=sort != "Highest price")
    st.subheader(f"{len(subset):,} matching properties")

    if subset.empty:
        st.info("Try increasing your budget or changing the filters.")
    else:
        pages = max(1, (len(subset) + 11) // 12)
        page_number = int(st.number_input("Page", min_value=1, max_value=pages, value=1))
        visible = subset.iloc[(page_number-1)*12:page_number*12]
        columns = st.columns(3)
        for index, (_, row) in enumerate(visible.iterrows()):
            esc = lambda value: html.escape(str(value))
            with columns[index % 3]:
                st.markdown(f"""
                <div class="property">
                  <div class="tag">{esc(row['Property_Type'])} · ID {esc(row['ID'])}</div>
                  <h3>{esc(row['City'])}</h3>
                  <p>{esc(row['Locality'])} · {esc(row['State'])}</p>
                  <div class="price">{money(row['Price_in_Lakhs'])}</div>
                  <p>{esc(row['BHK'])} BHK · {row['Size_in_SqFt']:,.0f} sq ft<br>
                  ₹{row['Price_per_SqFt']:,.0f} / sq ft</p>
                  <div class="tag">{esc(row['Availability_Status'])}</div>
                </div>
                """, unsafe_allow_html=True)
        st.download_button(
            "Download filtered properties",
            subset.to_csv(index=False).encode("utf-8"),
            "estatevision_filtered.csv",
            "text/csv"
        )

elif page == "Investment Advisor":
    render_advisor(df)

elif page == "EDA Lab":
    render_eda(df)

elif page == "Market Intelligence":
    st.title("The market, in perspective.")
    city = st.selectbox("Market", ["All India"] + sorted(df["City"].dropna().unique().tolist()))
    view = df if city == "All India" else df[df["City"] == city]
    sample = view.sample(min(5000,len(view)), random_state=42)

    a,b,c = st.columns(3)
    a.metric("Properties", f"{len(view):,}")
    b.metric("Median price", money(view["Price_in_Lakhs"].median()))
    c.metric("Median ₹ / sq ft", f"₹{view['Price_per_SqFt'].median():,.0f}")

    left,right = st.columns(2)
    with left:
        chart(px.histogram(view, x="Price_in_Lakhs", nbins=50,
            title="Asking price distribution",
            labels={"Price_in_Lakhs":"Price (₹ lakhs)"}))
        chart(px.box(view, x="Property_Type", y="Price_per_SqFt",
            title="Price per sq ft by property type", points=False))
    with right:
        chart(px.scatter(sample, x="Size_in_SqFt", y="Price_in_Lakhs",
            color="Property_Type", opacity=.45,
            title="Size and asking price · up to 5,000 sampled records"))
        chart(px.box(view, x="Furnished_Status", y="Price_in_Lakhs",
            title="Prices by furnishing status", points=False))
    st.caption("These charts describe the supplied dataset. It contains no dated sales history, so they do not establish market growth over time.")

elif page == "Growth Simulator":
    st.title("Imagine the next five years.")
    st.caption("Illustrative scenario calculator · not a trained model forecast")
    a,b = st.columns(2)
    price = a.number_input("Current property price (₹ lakhs)", min_value=1.0, value=80.0, step=5.0)
    rate = b.slider("Assumed annual price change (%)", -15.0, 20.0, 6.0, .5)
    years = list(range(6))
    values = [price * (1 + rate/100)**year for year in years]
    a,b,c = st.columns(3)
    a.metric("Current value", money(price))
    b.metric("Year-five scenario", money(values[-1]))
    c.metric("Total change", f"{(values[-1]/price-1)*100:+.1f}%")
    chart(px.area(x=years, y=values,
        labels={"x":"Years from now", "y":"Scenario value (₹ lakhs)"},
        title="Compound-growth scenario"))
    st.info("The annual rate is your assumption. This calculation excludes rent, purchase and sale costs, taxes, maintenance, inflation, and financing.")

else:
    st.title("Know the data behind the view.")
    report = ROOT / "reports/data_quality.json"
    if report.exists():
        import json
        quality = json.loads(report.read_text(encoding="utf-8"))
        a,b,c = st.columns(3)
        a.metric("Source records", f"{quality['source_rows']:,}")
        b.metric("Floor inconsistencies", f"{quality['inconsistent_floor_rows']:,}")
        c.metric("Price outliers flagged", f"{quality['price_outliers_flagged']:,}")
        st.json(quality)
    st.markdown("""
**Price units:** asking prices are in lakhs; price per square foot is recalculated in rupees.

**Floor inconsistencies:** affected floor values are marked missing.

**Outliers:** flagged for inspection and retained.

**Coverage:** dataset records are not verified current listings.

**Future prices:** no observed five-year outcomes are supplied.
""")
