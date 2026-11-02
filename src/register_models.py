from pathlib import Path
import json
import joblib
import mlflow
import mlflow.sklearn

ROOT = Path(__file__).resolve().parents[1]
TRUSTED = ["numpy.dtype", "sklearn.tree._tree.Tree"]

def main():
    # Fix future training runs too.
    training = ROOT / "src/train_models.py"
    text = training.read_text(encoding="utf-8-sig")
    marker = 'registered_model_name="EstateVision_" + name'
    if "skops_trusted_types=" not in text:
        if marker not in text:
            raise RuntimeError("Could not locate model registration code.")
        text = text.replace(
            marker,
            marker + ',\n                skops_trusted_types=' + repr(TRUSTED)
        )
        training.write_text(text, encoding="utf-8")

    metrics_path = ROOT / "reports/model_metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    database = (ROOT / "mlflow.db").resolve().as_posix()
    mlflow.set_tracking_uri("sqlite:///" + database)
    mlflow.set_experiment("EstateVision_AI")

    tasks = [
        ("investment_classifier", "classification"),
        ("future_value_regressor", "regression_scenario")
    ]

    for name, metric_key in tasks:
        print(f"Registering {name}...", flush=True)

        # Load only the local models created by our training script.
        model = joblib.load(ROOT / "models" / f"{name}.joblib")

        with mlflow.start_run(run_name=name + "_registration_fix"):
            mlflow.log_param("source", "locally_trained_model")
            mlflow.log_metrics(metrics[metric_key])
            mlflow.log_artifact(str(metrics_path))
            mlflow.log_artifact(str(ROOT / "models/metadata.json"))
            mlflow.sklearn.log_model(
                model,
                name="model",
                registered_model_name="EstateVision_" + name,
                skops_trusted_types=TRUSTED
            )

        print(f"Registered: {name}", flush=True)

    print("\nMLFLOW REGISTRATION COMPLETE", flush=True)

if __name__ == "__main__":
    main()
