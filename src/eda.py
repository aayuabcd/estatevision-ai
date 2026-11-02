from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

QUESTIONS = [
    "1. Distribution of property prices",
    "2. Distribution of property sizes",
    "3. Price per sq ft by property type",
    "4. Relationship between size and price",
    "5. Outliers in price per sq ft and size",
    "6. Average price per sq ft by state",
    "7. Average property price by city",
    "8. Median property age by locality",
    "9. BHK distribution across cities",
    "10. Five most expensive localities",
    "11. Correlation between numeric features",
    "12. Nearby schools and price per sq ft",
    "13. Nearby hospitals and price per sq ft",
    "14. Price by furnished status",
    "15. Price per sq ft by facing direction",
    "16. Property counts by owner type",
    "17. Property counts by availability",
    "18. Parking and property price",
    "19. Amenities and price per sq ft",
    "20. Transport access and price per sq ft"
]

def grouped(df, keys, value, operation="mean"):
    return df.groupby(keys, dropna=False)[value].agg(
        operation
    ).reset_index()

def outlier_summary(df):
    records = []
    for column in ["Price_per_SqFt", "Size_in_SqFt"]:
        q1, q3 = df[column].quantile([.25, .75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
        count = int(((df[column] < lower) | (df[column] > upper)).sum())
        records.append({
            "Feature": column,
            "Lower bound": lower,
            "Upper bound": upper,
            "Outliers": count,
            "Percentage": 100*count/len(df)
        })
    return pd.DataFrame(records)

def analysis(df, number):
    price = "Price_in_Lakhs"
    sqft = "Price_per_SqFt"
    sample = df.sample(min(5000, len(df)), random_state=42)
    note = "These are descriptive associations in the supplied dataset, not causal effects."

    if number in [1, 2]:
        column = price if number == 1 else "Size_in_SqFt"
        table = df[column].describe().rename("Value").reset_index()
        fig = px.histogram(df, x=column, nbins=50)
        note = f"Median: {df[column].median():,.2f}; mean: {df[column].mean():,.2f}. Prices are in lakhs; sizes are in sq ft."

    elif number == 3:
        table = grouped(df, "Property_Type", sqft, "median")
        fig = px.box(sample, x="Property_Type", y=sqft, points=False)
        note = "Table uses all records; box plot uses a reproducible sample of up to 5,000 records."

    elif number == 4:
        table = pd.DataFrame({
            "Statistic": ["Pearson correlation: size vs price"],
            "Value": [df["Size_in_SqFt"].corr(df[price])]
        })
        fig = px.scatter(sample, x="Size_in_SqFt", y=price, opacity=.4)
        note = "Correlation uses all records. The scatter plot samples up to 5,000 records."

    elif number == 5:
        table = outlier_summary(df)
        fig = px.bar(table, x="Feature", y="Outliers")
        note = "Outliers use the 1.5 × IQR rule. Flagging a record does not prove it is incorrect."

    elif number in [6, 7, 8, 10]:
        if number == 6:
            keys, value, operation = ["State"], sqft, "mean"
        elif number == 7:
            keys, value, operation = ["City"], price, "mean"
        elif number == 8:
            keys, value, operation = ["State", "City", "Locality"], "Age_of_Property", "median"
        else:
            keys, value, operation = ["State", "City", "Locality"], price, "mean"

        table = grouped(df, keys, value, operation).sort_values(
            value, ascending=False
        )
        if number == 10:
            table = table.head(5)
            note = (
                "Top five localities by mean asking price. Historical price "
                "trends cannot be calculated: no dated price history is supplied."
            )
        elif number == 8:
            note = (
                "Localities are identified by state, city, and locality together. "
                "Age retains the dataset's original reference date. "
                "The chart shows the 25 highest median ages; the table includes all localities."
            )
        chart_data = table.head(25).copy()
        chart_data["Location"] = chart_data[keys].astype(str).agg(" / ".join, axis=1)
        fig = px.bar(chart_data, x=value, y="Location", orientation="h")

    elif number == 9:
        table = df.groupby(["City", "BHK"]).size().reset_index(name="Properties")
        fig = px.bar(table, x="City", y="Properties", color="BHK", barmode="stack")

    elif number == 11:
        columns = [
            price, "Size_in_SqFt", sqft, "BHK", "Age_of_Property",
            "Nearby_Schools", "Nearby_Hospitals", "Amenity_Count",
            "Has_Parking", "Has_Security"
        ]
        table = df[columns].corr()
        fig = px.imshow(
            table, zmin=-1, zmax=1,
            color_continuous_scale="RdBu_r", aspect="auto"
        )
        note = "Pearson correlations. Price per sq ft is derived from price and size, so related correlations need careful interpretation."

    elif number in [12, 13]:
        column = "Nearby_Schools" if number == 12 else "Nearby_Hospitals"
        table = grouped(df, column, sqft)
        fig = px.line(table, x=column, y=sqft, markers=True)
        note = (
            f"Pearson correlation with price per sq ft: "
            f"{df[column].corr(df[sqft]):.4f}. "
            "The chart shows group means, not a causal effect."
        )

    elif number in [14, 15, 18, 20]:
        column, value = {
            14: ("Furnished_Status", price),
            15: ("Facing", sqft),
            18: ("Parking_Space", price),
            20: ("Public_Transport_Accessibility", sqft)
        }[number]
        table = df.groupby(column)[value].agg(
            ["count", "mean", "median"]
        ).reset_index()
        fig = px.bar(table, x=column, y="mean")
        if number == 20:
            note = (
                "Transport groups are compared using price per sq ft. "
                "Real investment returns are not observed in this dataset."
            )

    elif number in [16, 17]:
        column = "Owner_Type" if number == 16 else "Availability_Status"
        table = df[column].value_counts().rename_axis(
            column
        ).reset_index(name="Properties")
        fig = px.bar(table, x=column, y="Properties")

    else:
        expanded = df[["Amenities", sqft]].copy()
        expanded["Amenity"] = expanded["Amenities"].fillna("").map(
            lambda value: sorted({
                item.strip() for item in str(value).split(",")
                if item.strip()
            })
        )
        expanded = expanded.explode("Amenity").dropna(subset=["Amenity"])
        table = expanded.groupby("Amenity")[sqft].agg(
            ["count", "mean", "median"]
        ).reset_index()
        fig = px.bar(table, x="Amenity", y="mean")
        note = (
            "A property can appear in multiple amenity groups. "
            "These comparisons do not isolate the effect of an amenity."
        )

    return table, fig, note

def render_eda(df):
    st.title("Explore the evidence.")
    st.caption("All 20 EDA questions from the project brief.")
    city = st.selectbox(
        "Analysis scope",
        ["All India"] + sorted(df["City"].dropna().unique().tolist()),
        key="eda_city"
    )
    view = df if city == "All India" else df[df["City"] == city]
    question = st.selectbox("Choose a question", QUESTIONS)
    number = QUESTIONS.index(question) + 1

    st.subheader(question)
    table, fig, note = analysis(view, number)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce6f5"),
        colorway=["#7ce7df", "#ae91ff", "#ffb99f"],
        height=520
    )
    st.plotly_chart(fig, width="stretch")
    st.info(note)
    st.dataframe(table, width="stretch")
    st.download_button(
        "Download this analysis",
        table.to_csv(index=(number == 11)).encode("utf-8"),
        f"eda_question_{number:02d}.csv",
        "text/csv"
    )

def export_all():
    root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(root / "data/processed/housing_cleaned.csv")
    output = root / "reports/eda"
    output.mkdir(parents=True, exist_ok=True)
    findings = ["# EstateVision AI: EDA findings", ""]
    for number, question in enumerate(QUESTIONS, start=1):
        table, fig, note = analysis(df, number)
        table.to_csv(
            output / f"question_{number:02d}.csv",
            index=(number == 11)
        )
        findings.extend([
            f"## {question}", "",
            note, "",
            "```text",
            table.head(10).round(4).to_string(index=(number == 11)),
            "```", ""
        ])
        print(f"Exported question {number}/20", flush=True)
    (output / "findings.md").write_text(
        "\n".join(findings), encoding="utf-8"
    )
    print("ALL 20 EDA ANALYSES EXPORTED")

if __name__ == "__main__":
    export_all()
