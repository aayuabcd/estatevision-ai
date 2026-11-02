from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"
RATE = 0.06
SEED = 42

NUMERIC = [
    "Price_in_Lakhs", "Size_in_SqFt", "BHK",
    "Age_of_Property", "Nearby_Schools", "Nearby_Hospitals",
    "Amenity_Count", "Has_Parking", "Has_Security"
]
CATEGORICAL = [
    "City", "Property_Type", "Furnished_Status",
    "Public_Transport_Accessibility", "Availability_Status"
]
FEATURES = NUMERIC + CATEGORICAL

def preprocessing():
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore"))
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC),
        ("categorical", categorical, CATEGORICAL)
    ])

def investment_labels(frame, city_reference, fallback):
    reference = frame["City"].map(city_reference).fillna(fallback)
    affordable = (
        frame["Price_in_Lakhs"] * 100000 / frame["Size_in_SqFt"]
    ).le(reference)

    # Defined screening rule, not observed investment profitability.
    score = (
        affordable.astype(int) * 2
        + frame["Has_Parking"].fillna(0)
        + frame["Has_Security"].fillna(0)
        + frame["Transport_Score"].fillna(0).ge(2).astype(int)
        + frame["Availability_Status"].eq("Ready_to_Move").astype(int)
    )
    return score.ge(4).astype(int)

def regression_metrics(actual, predicted):
    return {
        "mae_lakhs": float(mean_absolute_error(actual, predicted)),
        "rmse_lakhs": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted))
    }

def main():
    MODELS.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)

    print("1/5 Loading cleaned data...", flush=True)
    df = pd.read_csv(ROOT / "data/processed/housing_cleaned.csv")

    # Bounded sample keeps training manageable on a student laptop.
    sample = df.sample(n=min(50000, len(df)), random_state=SEED)
    train, test = train_test_split(
        sample, test_size=0.2, random_state=SEED
    )

    # Reference values are fitted on training records only.
    city_reference = train.groupby("City")["Price_per_SqFt"].median()
    fallback = float(train["Price_per_SqFt"].median())

    y_train_class = investment_labels(train, city_reference, fallback)
    y_test_class = investment_labels(test, city_reference, fallback)

    if y_train_class.nunique() < 2:
        raise ValueError("Investment labels need both classes.")

    factor = (1 + RATE) ** 5
    y_train_reg = train["Price_in_Lakhs"] * factor
    y_test_reg = test["Price_in_Lakhs"] * factor

    X_train = train[FEATURES].copy()
    X_test = test[FEATURES].copy()

    classifier = Pipeline([
        ("preprocess", preprocessing()),
        ("model", RandomForestClassifier(
            n_estimators=60, max_depth=16,
            min_samples_leaf=5, random_state=SEED,
            n_jobs=2, class_weight="balanced"
        ))
    ])
    regressor = Pipeline([
        ("preprocess", preprocessing()),
        ("model", RandomForestRegressor(
            n_estimators=60, max_depth=16,
            min_samples_leaf=5, random_state=SEED,
            n_jobs=2
        ))
    ])

    # Local SQLite backend supports experiment tracking and registration.
    database = (ROOT / "mlflow.db").resolve().as_posix()
    mlflow.set_tracking_uri("sqlite:///" + database)
    mlflow.set_experiment("EstateVision_AI")

    print("2/5 Training investment classifier...", flush=True)
    classifier.fit(X_train, y_train_class)
    class_predictions = classifier.predict(X_test)

    dummy_class = DummyClassifier(strategy="most_frequent")
    dummy_class.fit(X_train, y_train_class)
    dummy_predictions = dummy_class.predict(X_test)

    class_metrics = {
        "accuracy": float(accuracy_score(y_test_class, class_predictions)),
        "f1": float(f1_score(
            y_test_class, class_predictions, zero_division=0
        )),
        "baseline_accuracy": float(
            accuracy_score(y_test_class, dummy_predictions)
        ),
        "baseline_f1": float(
            f1_score(y_test_class, dummy_predictions, zero_division=0)
        )
    }

    matrix = confusion_matrix(
        y_test_class, class_predictions, labels=[0, 1]
    )
    pd.DataFrame(
        matrix,
        index=["Actual_Not_Selected", "Actual_Good_Investment"],
        columns=["Predicted_Not_Selected", "Predicted_Good_Investment"]
    ).to_csv(REPORTS / "confusion_matrix.csv")

    print("3/5 Training five-year scenario regressor...", flush=True)
    regressor.fit(X_train, y_train_reg)
    reg_predictions = regressor.predict(X_test)
    reg_metrics = regression_metrics(y_test_reg, reg_predictions)

    dummy_reg = DummyRegressor(strategy="mean")
    dummy_reg.fit(X_train, y_train_reg)
    baseline_reg = regression_metrics(
        y_test_reg, dummy_reg.predict(X_test)
    )

    # Exact formula is the appropriate benchmark for formula-created targets.
    formula_reg = regression_metrics(
        y_test_reg, X_test["Price_in_Lakhs"] * factor
    )

    print("4/5 Saving models, explanations, and reports...", flush=True)
    joblib.dump(classifier, MODELS / "investment_classifier.joblib")
    joblib.dump(regressor, MODELS / "future_value_regressor.joblib")

    metadata = {
        "features": FEATURES,
        "annual_growth_assumption": RATE,
        "years": 5,
        "train_rows": len(train),
        "test_rows": len(test),
        "random_seed": SEED,
        "training_sample_rows": len(sample),
        "city_price_per_sqft_reference": city_reference.to_dict(),
        "fallback_price_per_sqft": fallback,
        "classification_target": (
            "Rule-derived screening label: score >= 4; "
            "2 points for price/sqft <= training city median, "
            "1 each for parking, security, medium/high transport, "
            "and ready-to-move status."
        ),
        "regression_target": (
            "Synthetic scenario: current price * (1.06 ** 5). "
            "Current price is an input, so this evaluates formula "
            "approximation, not real future-price forecasting."
        ),
        "probability_note": (
            "Classifier probabilities are uncalibrated estimates "
            "of rule-label membership, not investment success."
        )
    }
    (MODELS / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    report = {
        "classification": class_metrics,
        "regression_scenario": reg_metrics,
        "regression_mean_baseline": baseline_reg,
        "regression_exact_formula_baseline": formula_reg,
        "limitations": [
            "Investment labels are generated from a screening rule.",
            "Future values are synthetic, not observed outcomes.",
            "The exact compound-growth formula is the preferred scenario calculation.",
            "No historical validation of investment returns is possible with this dataset."
        ]
    }
    (REPORTS / "model_metrics.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    for name, pipeline in [
        ("classification", classifier), ("regression", regressor)
    ]:
        names = pipeline.named_steps["preprocess"].get_feature_names_out()
        importance = pipeline.named_steps["model"].feature_importances_
        pd.DataFrame({
            "feature": names,
            "importance": importance
        }).sort_values("importance", ascending=False).to_csv(
            REPORTS / f"{name}_feature_importance.csv", index=False
        )

    pd.DataFrame({
        "ID": test["ID"].to_numpy(),
        "actual_rule_label": y_test_class.to_numpy(),
        "predicted_rule_label": class_predictions,
        "scenario_target_lakhs": y_test_reg.to_numpy(),
        "scenario_prediction_lakhs": reg_predictions
    }).to_csv(REPORTS / "test_predictions.csv", index=False)

    print("5/5 Logging experiments and registering models...", flush=True)
    for name, pipeline, metrics in [
        ("investment_classifier", classifier, class_metrics),
        ("future_value_regressor", regressor, reg_metrics)
    ]:
        with mlflow.start_run(run_name=name):
            mlflow.log_params({
                "train_rows": len(train),
                "test_rows": len(test),
                "seed": SEED,
                "trees": 60,
                "max_depth": 16,
                "target_type": "rule" if name == "investment_classifier" else "synthetic_scenario"
            })
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(REPORTS / "model_metrics.json"))
            mlflow.log_artifact(str(MODELS / "metadata.json"))
            mlflow.sklearn.log_model(
                pipeline,
                artifact_path="model",
                registered_model_name="EstateVision_" + name,
                skops_trusted_types=['numpy.dtype', 'sklearn.tree._tree.Tree']
            )

    print("\nTRAINING COMPLETE", flush=True)
    print(json.dumps(report, indent=2))
    print("\nModels saved in models/")
    print("Evaluation reports saved in reports/")
    print("MLflow experiments saved in local mlflow.db")

if __name__ == "__main__":
    main()
