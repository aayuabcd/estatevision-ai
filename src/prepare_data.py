from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/india_housing_prices.csv"
OUTPUT = ROOT / "data/processed"
REPORTS = ROOT / "reports"

def prepare():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(SOURCE)
    original_rows = len(df)

    # Standardize text without changing the source file.
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].astype("string").str.strip()

    # Remove repeated property records, ignoring the record ID.
    comparison_columns = [c for c in df.columns if c != "ID"]
    duplicate_count = int(df.duplicated(subset=comparison_columns).sum())
    df = df.drop_duplicates(subset=comparison_columns).copy()

    numeric_columns = [
        "BHK", "Size_in_SqFt", "Price_in_Lakhs", "Year_Built",
        "Floor_No", "Total_Floors", "Age_of_Property",
        "Nearby_Schools", "Nearby_Hospitals"
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    valid = (
        df["Price_in_Lakhs"].gt(0)
        & df["Size_in_SqFt"].gt(0)
        & df["BHK"].gt(0)
    )
    invalid_count = int((~valid).sum())
    df = df.loc[valid].copy()

    # Source prices are in lakhs; convert to rupees per square foot.
    df["Source_Price_per_SqFt"] = df["Price_per_SqFt"]
    df["Price_per_SqFt"] = (
        df["Price_in_Lakhs"] * 100000 / df["Size_in_SqFt"]
    ).round(2)

    df["Floor_Inconsistent"] = (
        df["Floor_No"].gt(df["Total_Floors"])
        | df["Floor_No"].lt(0)
        | df["Total_Floors"].lt(1)
    )
    floor_issues = int(df["Floor_Inconsistent"].sum())

    # Preserve the flag and avoid treating inconsistent floors as valid.
    df.loc[df["Floor_Inconsistent"], "Floor_No"] = float("nan")

    df["Amenity_Count"] = df["Amenities"].fillna("").map(
        lambda value: len({
            item.strip().lower()
            for item in str(value).split(",")
            if item.strip()
        })
    )
    df["Has_Parking"] = (
        df["Parking_Space"].str.lower().eq("yes").fillna(False).astype(int)
    )
    df["Has_Security"] = (
        df["Security"].str.lower().eq("yes").fillna(False).astype(int)
    )
    df["Transport_Score"] = (
        df["Public_Transport_Accessibility"].str.lower()
        .map({"low": 1, "medium": 2, "high": 3})
    )
    df["School_Density_Per_1000_SqFt"] = (
        df["Nearby_Schools"] / df["Size_in_SqFt"] * 1000
    ).round(3)

    # Flag statistical extremes for analysis; retain valid expensive homes.
    low, high = df["Price_per_SqFt"].quantile([0.25, 0.75])
    spread = high - low
    df["Price_Outlier"] = (
        df["Price_per_SqFt"].lt(low - 1.5 * spread)
        | df["Price_per_SqFt"].gt(high + 1.5 * spread)
    )

    cleaned_path = OUTPUT / "housing_cleaned.csv"
    df.to_csv(cleaned_path, index=False)

    summary = {
        "source_rows": original_rows,
        "cleaned_rows": len(df),
        "duplicates_removed": duplicate_count,
        "invalid_price_size_bhk_rows_removed": invalid_count,
        "inconsistent_floor_rows": floor_issues,
        "price_outliers_flagged": int(df["Price_Outlier"].sum()),
        "cities": int(df["City"].nunique()),
        "states": int(df["State"].nunique()),
        "missing_values_after_cleaning": {
            key: int(value) for key, value in df.isna().sum().items()
        },
        "notes": [
            "Price_per_SqFt is expressed in rupees.",
            "Inconsistent Floor_No values are missing and flagged.",
            "Age_of_Property retains the dataset's original reference date.",
            "No observed future prices exist in the source dataset.",
            "Model preprocessing must be fitted only on training data."
        ]
    }
    (REPORTS / "data_quality.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print("DATA PREPARATION COMPLETE")
    for key in [
        "source_rows", "cleaned_rows", "duplicates_removed",
        "invalid_price_size_bhk_rows_removed",
        "inconsistent_floor_rows", "price_outliers_flagged",
        "cities", "states"
    ]:
        print(f"{key}: {summary[key]}")
    print(f"Saved: {cleaned_path}")
    print("Saved: reports/data_quality.json")

if __name__ == "__main__":
    prepare()
