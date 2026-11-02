import html
import streamlit as st

def cinematic_home(df):
    st.markdown("""
    <style>
    [data-testid="stHeader"] {
        background:rgba(8,13,23,.94) !important;
    }
    [data-testid="stSidebar"] * {color:#dce5f5;}
    [data-testid="stMetricLabel"] p {color:#b9c9df !important;}
    .stApp {color:#eef3ff;}
    .block-container {padding-top:2rem;max-width:1560px;}
    .ev-nav {
        display:flex;justify-content:space-between;align-items:center;
        padding:0 4px 22px;color:#eaf2ff;
    }
    .ev-brand {font-size:21px;font-weight:700;letter-spacing:-1px;}
    .ev-brand span {color:#92f4cf;}
    .ev-nav small {font-size:10px;letter-spacing:2px;color:#a1b5c9;}
    .ev-scene {
        min-height:560px;position:relative;overflow:hidden;
        border:1px solid #ffffff21;border-radius:24px;
        background:
          radial-gradient(ellipse at 78% 32%,#a58ac933,transparent 42%),
          linear-gradient(145deg,#102c38,#101a2b 45%,#251e3c);
        margin-bottom:26px;
    }
    .ev-content {
        position:relative;z-index:3;padding:58px 46px;
        max-width:70%;
    }
    .ev-kicker {
        display:inline-block;border:1px solid #a6f4d23b;
        padding:8px 13px;border-radius:30px;color:#a6f4d2;
        font-size:10px;letter-spacing:2px;
    }
    .ev-content h1 {
        color:#f4f4ed !important;font-size:clamp(44px,5.5vw,78px);
        font-weight:500;line-height:1.02;letter-spacing:-4px;
        margin:25px 0 22px;
    }
    .ev-content h1 em {
        color:#a6f4d2;font-family:Georgia,serif;font-weight:400;
    }
    .ev-content p {
        max-width:420px;color:#c1d1df;font-size:15px;line-height:1.8;
    }
    .ev-caption {
        margin-top:34px;font-size:10px;letter-spacing:2px;color:#92adbf;
    }
    .ev-orbit {
        width:330px;height:330px;position:absolute;right:8%;top:12%;
        border:1px solid #d6c4ff40;border-radius:50%;
        box-shadow:0 0 100px #bca0ff12,inset 0 0 100px #bca0ff0c;
        animation:ev-breathe 8s ease-in-out infinite alternate;
    }
    .ev-orbit:after {
        content:"";position:absolute;inset:25px;
        border:1px dashed #ffffff19;border-radius:50%;
    }
    .ev-city {
        position:absolute;right:0;bottom:0;width:53%;height:82%;
        display:flex;align-items:flex-end;justify-content:center;
        gap:9px;transform:skewY(-7deg);
        mask-image:linear-gradient(to bottom,#000 75%,transparent);
    }
    .ev-building {
        position:relative;width:18%;height:var(--height);
        border:1px solid #b4e7e34a;border-top:2px solid #c5fff1aa;
        background:
          repeating-linear-gradient(0deg,transparent 0 19px,#9ce9d62e 20px 21px),
          repeating-linear-gradient(90deg,#152b3d 0 13px,#97e0d526 14px 15px);
        box-shadow:14px 12px 0 #07152270;
        animation:ev-rise 1.3s ease-out both;
    }
    .ev-building:nth-child(2) {animation-delay:.12s;}
    .ev-building:nth-child(3) {animation-delay:.24s;}
    .ev-building:nth-child(4) {animation-delay:.36s;}
    .ev-building:before {
        content:"";position:absolute;top:-15px;left:12%;right:12%;
        height:14px;background:#203f50;border:1px solid #c1ffe14a;
    }
    .ev-city-label {
        position:absolute;right:25px;bottom:24px;z-index:4;
        color:#d6e6ef;font-size:9px;letter-spacing:2px;
    }
    .ev-float {
        position:absolute;right:6%;top:40%;z-index:4;
        padding:17px 22px;background:#0b1829df;
        border:1px solid #c4fff13b;border-radius:14px;
        box-shadow:0 20px 50px #0005;
        animation:ev-float 6s ease-in-out infinite;
    }
    .ev-float small {font-size:9px;letter-spacing:2px;color:#9ab6c5;}
    .ev-float strong {display:block;font-size:26px;color:#b2f7d8;margin-top:5px;}
    .ev-strip {
        display:flex;gap:25px;flex-wrap:wrap;padding:15px 4px 25px;
        color:#93aabd;font-size:10px;letter-spacing:2px;
    }
    .ev-strip span:before {content:"✦ ";color:#a6f4d2;}
    .ev-spotlight {
        padding:22px 25px;border-radius:15px;
        border:1px solid #ffffff1b;background:#ffffff05;
        margin:8px 0 20px;
    }
    .ev-spotlight h3 {color:#a6f4d2 !important;margin:0 0 8px;}
    .ev-spotlight p {color:#c0cede;margin:0;line-height:1.7;}
    @keyframes ev-rise {
        from {opacity:0;translate:0 70px;} to {opacity:1;translate:0 0;}
    }
    @keyframes ev-float {
        0%,100% {translate:0 0;} 50% {translate:0 -10px;}
    }
    @keyframes ev-breathe {
        from {scale:.95;opacity:.5;} to {scale:1.05;opacity:1;}
    }
    @media(max-width:900px) {
        .ev-content {max-width:100%;padding:34px 25px;}
        .ev-content h1 {letter-spacing:-2px;}
        .ev-content p {max-width:75%;}
        .ev-city {opacity:.25;width:65%;}
        .ev-float {display:none;}
        .ev-orbit {right:-130px;}
        .ev-nav small {display:none;}
    }
    @media(prefers-reduced-motion:reduce) {
        .ev-building,.ev-float,.ev-orbit {animation:none;}
    }
    </style>
    """, unsafe_allow_html=True)

    cities = df["City"].nunique()
    st.markdown(f"""
    <div class="ev-nav">
      <div class="ev-brand">estate<span>vision</span> / AI</div>
      <small>EXPLORE SPACES. UNDERSTAND POSSIBILITIES.</small>
    </div>
    <div class="ev-scene">
      <div class="ev-orbit"></div>
      <div class="ev-city" aria-hidden="true">
        <div class="ev-building" style="--height:38%"></div>
        <div class="ev-building" style="--height:67%"></div>
        <div class="ev-building" style="--height:88%"></div>
        <div class="ev-building" style="--height:55%"></div>
      </div>
      <div class="ev-content">
        <div class="ev-kicker">A NEW PERSPECTIVE ON PROPERTY</div>
        <h1>Spaces to live.<br>Possibilities<br>to <em>discover.</em></h1>
        <p>Your next chapter starts with a clearer view.
        Explore India's housing landscape through property discovery,
        market insights, and interactive scenarios.</p>
        <div class="ev-caption">PROPERTY DISCOVERY / MARKET ANALYTICS / FUTURE SCENARIOS</div>
      </div>
      <div class="ev-float">
        <small>YOUR EXPLORATION CANVAS</small>
        <strong>{cities} Indian cities</strong>
      </div>
      <div class="ev-city-label">ARCHITECTURAL ILLUSTRATION · NOT A PROPERTY LISTING</div>
    </div>
    <div class="ev-strip">
      <span>EXPLORE WITH CONTEXT</span>
      <span>COMPARE WITH CLARITY</span>
      <span>IMAGINE WHAT COMES NEXT</span>
    </div>
    """, unsafe_allow_html=True)

    a, b = st.columns([1, 2])
    with a:
        city = st.selectbox(
            "Choose your city spotlight",
            sorted(df["City"].dropna().unique().tolist()),
            key="home_spotlight"
        )
    view = df[df["City"] == city]
    median = view["Price_in_Lakhs"].median()
    sqft = view["Price_per_SqFt"].median()
    with b:
        safe_city = html.escape(str(city))
        st.markdown(f"""
        <div class="ev-spotlight">
          <h3>{safe_city}, in focus.</h3>
          <p>{len(view):,} dataset listings · Median asking price
          ₹{median:,.2f} lakhs · Median ₹{sqft:,.0f} / sq ft</p>
        </div>
        """, unsafe_allow_html=True)
