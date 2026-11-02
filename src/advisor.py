from pathlib import Path
import json
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

@st.cache_resource
def load_models(classifier_time, regressor_time, metadata_time):
    classifier = joblib.load(ROOT / "models/investment_classifier.joblib")
    regressor = joblib.load(ROOT / "models/future_value_regressor.joblib")
    metadata = json.loads(
        (ROOT / "models/metadata.json").read_text(encoding="utf-8")
    )
    return classifier, regressor, metadata

def render_advisor(df):
    st.title("Your property. A clearer assessment.")
    st.caption("Trained model screening, transparent criteria, and five-year scenarios.")

    paths = [
        ROOT / "models/investment_classifier.joblib",
        ROOT / "models/future_value_regressor.joblib",
        ROOT / "models/metadata.json"
    ]
    if not all(path.exists() for path in paths):
        st.error("Model files are missing. Complete model training first.")
        return

    classifier, regressor, metadata = load_models(
        *(path.stat().st_mtime for path in paths)
    )

    def choices(column):
        return sorted(df[column].dropna().unique().tolist())

    with st.form("property_assessment"):
        a, b, c = st.columns(3)
        city = a.selectbox("City", choices("City"))
        kind = b.selectbox("Property type", choices("Property_Type"))
        furnished = c.selectbox("Furnishing", choices("Furnished_Status"))

        a, b, c = st.columns(3)
        price = a.number_input(
            "Asking price (₹ lakhs)", min_value=1.0, value=80.0, step=5.0
        )
        size = b.number_input(
            "Property size (sq ft)", min_value=100, value=1200, step=100
        )
        bhk = c.number_input("BHK", min_value=1, max_value=20, value=2)

        a, b, c = st.columns(3)
        age = a.number_input(
            "Property age (years)", min_value=0, max_value=150, value=5
        )
        schools = b.number_input(
            "Nearby schools", min_value=0, max_value=100, value=3
        )
        hospitals = c.number_input(
            "Nearby hospitals", min_value=0, max_value=100, value=2
        )

        a, b, c = st.columns(3)
        transport = a.selectbox(
            "Public transport access", choices("Public_Transport_Accessibility")
        )
        availability = b.selectbox(
            "Availability", choices("Availability_Status")
        )
        amenity_count = c.number_input(
            "Number of amenities", min_value=0, max_value=30, value=3
        )

        a, b = st.columns(2)
        parking = a.checkbox("Parking available", value=True)
        security = b.checkbox("Security available", value=True)

        submitted = st.form_submit_button(
            "Assess this property", use_container_width=True
        )

    if submitted:
        row = pd.DataFrame([{
            "Price_in_Lakhs": price,
            "Size_in_SqFt": size,
            "BHK": bhk,
            "Age_of_Property": age,
            "Nearby_Schools": schools,
            "Nearby_Hospitals": hospitals,
            "Amenity_Count": amenity_count,
            "Has_Parking": int(parking),
            "Has_Security": int(security),
            "City": city,
            "Property_Type": kind,
            "Furnished_Status": furnished,
            "Public_Transport_Accessibility": transport,
            "Availability_Status": availability
        }])[metadata["features"]]

        label = int(classifier.predict(row)[0])
        classes = list(classifier.classes_)
        probability = float(
            classifier.predict_proba(row)[0, classes.index(1)]
        )
        model_value = float(regressor.predict(row)[0])
        rate = metadata["annual_growth_assumption"]
        years = metadata["years"]
        formula_value = price * (1 + rate) ** years

        a, b, c = st.columns(3)
        a.metric(
            "Model screening",
            "Selected" if label else "Not selected"
        )
        b.metric("Rule-label probability", f"{probability:.1%}")
        c.metric("Five-year ML scenario", f"₹{model_value:,.2f} L")

        st.caption(
            "Probability estimates membership in the defined screening label. "
            "It is uncalibrated and does not estimate investment success."
        )

        reference = metadata["city_price_per_sqft_reference"].get(
            city, metadata["fallback_price_per_sqft"]
        )
        price_sqft = price * 100000 / size
        affordable = price_sqft <= reference
        good_transport = str(transport).lower() in ["medium", "high"]
        ready = availability == "Ready_to_Move"

        criteria = pd.DataFrame([
            {
                "Criterion": "Price/sq ft at or below training city median",
                "Met": affordable,
                "Points": 2 if affordable else 0
            },
            {"Criterion": "Parking", "Met": parking, "Points": int(parking)},
            {"Criterion": "Security", "Met": security, "Points": int(security)},
            {
                "Criterion": "Medium/high transport access",
                "Met": good_transport,
                "Points": int(good_transport)
            },
            {"Criterion": "Ready to move", "Met": ready, "Points": int(ready)}
        ])
        score = int(criteria["Points"].sum())

        st.subheader("Understand the screening criteria")
        st.write(
            f"Your price: ₹{price_sqft:,.0f}/sq ft · "
            f"Training city median: ₹{reference:,.0f}/sq ft"
        )
        st.dataframe(criteria, hide_index=True, use_container_width=True)
        st.write(f"Defined rule score: **{score}/6** · Selection threshold: **4**")

        rule_label = int(score >= 4)
        if label != rule_label:
            st.info(
                "The model prediction differs from the exact screening rule. "
                "The model approximates these criteria and can make errors."
            )

        st.subheader("Five-year scenario")
        st.write(
            f"At the assumed {rate:.0%} annual growth rate, the exact "
            f"compound-growth calculation gives **₹{formula_value:,.2f} lakhs**. "
            f"The trained model approximates it as **₹{model_value:,.2f} lakhs**."
        )
        trajectory = pd.DataFrame({
            "Year": list(range(years + 1)),
            "Value (₹ lakhs)": [
                price * (1 + rate) **year for year in range(years + 1)
            ]
        })
        fig = px.area(
            trajectory, x="Year", y="Value (₹ lakhs)",
            template="plotly_dark",
            title="Assumption-based compound-growth trajectory"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

        result = row.copy()
        result["Model_Selected"] = label
        result["Rule_Label_Probability"] = probability
        result["Exact_Rule_Score"] = score
        result["ML_Scenario_Lakhs"] = model_value
        result["Formula_Scenario_Lakhs"] = formula_value
        st.session_state["assessment_download"] = result.to_csv(
            index=False
        ).encode("utf-8")

    if "assessment_download" in st.session_state:
        st.download_button(
            "Download last assessment",
            st.session_state["assessment_download"],
            "estatevision_assessment.csv",
            "text/csv"
        )

    st.info(
        "Investment labels are based on defined screening criteria. "
        "Five-year targets use an assumed growth rate, not observed future "
        "sales. These results do not validate actual future profitability."
    )

    with st.expander("Model evaluation and feature importance"):
        metrics = ROOT / "reports/model_metrics.json"
        if metrics.exists():
            st.json(json.loads(metrics.read_text(encoding="utf-8")))

        st.caption(
            "Classification metrics measure agreement with rule-derived labels. "
            "Regression metrics measure approximation of synthetic scenarios."
        )

        matrix = ROOT / "reports/confusion_matrix.csv"
        if matrix.exists():
            st.subheader("Classification confusion matrix")
            st.dataframe(pd.read_csv(matrix, index_col=0))

        for task in ["classification", "regression"]:
            path = ROOT / f"reports/{task}_feature_importance.csv"
            if path.exists():
                importance = pd.read_csv(path).head(12)
                fig = px.bar(
                    importance.sort_values("importance"),
                    x="importance", y="feature", orientation="h",
                    title=f"{task.title()}: global feature importance",
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Feature importance describes global model behaviour, "
            "not a causal explanation of an individual property."
        )
