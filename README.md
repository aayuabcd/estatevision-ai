# EstateVision AI

## Real Estate Investment Advisor
Predicting Property Profitability & Future Value

Developed by Aayushi Suryawanshi.

## Overview
EstateVision AI is a Streamlit application for exploring Indian housing
data, screening properties against defined investment criteria, and
illustrating five-year property-value scenarios.

## Features
- Cinematic homepage with an interactive city spotlight
- Property explorer with location, budget, BHK, and size filters
- Classification-based property screening
- Five-year assumption-based regression scenarios
- Screening criteria and downloadable assessments
- Model evaluation, confusion matrix, and global feature importance
- Market analytics and an adjustable growth simulator
- EDA Lab addressing all 20 project questions
- Data-quality reporting
- MLflow experiment tracking and model registration

## Dataset
Source: india_housing_prices.csv, supplied with the project brief.

Download:
https://drive.google.com/file/d/1ys25Eaqo2n8IeHhyI9s0kmJBgnNzxQHX/view

The supplied dataset contains 250,000 records, 23 original columns,
42 cities, and 20 states.

Place the downloaded file at:
data/raw/india_housing_prices.csv

Raw data, processed data, trained model binaries, and the local MLflow
database are excluded from Git. They can be regenerated locally.

## Setup — Windows PowerShell
Use Python 3.11.

    py -3.11 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

## Prepare Data
    .\.venv\Scripts\python.exe src/prepare_data.py

The script standardizes text, removes duplicate records, validates
positive prices and sizes, recalculates rupee prices per square foot,
flags inconsistent floors, engineers features, and flags IQR outliers.

In the supplied run:
- 250,000 records were retained.
- 116,304 floor inconsistencies were flagged.
- 19,723 price-per-square-foot outliers were flagged.
- Invalid floor numbers were marked missing.
- Price outliers were retained for inspection.

## Train and Evaluate
    .\.venv\Scripts\python.exe src/train_models.py

Training uses a reproducible sample of up to 50,000 records,
an 80/20 train-test split, and random seed 42.

Models:
- RandomForestClassifier
- RandomForestRegressor

Preprocessing is fitted on training records only:
- Median numerical imputation
- Numerical standardization
- Most-frequent categorical imputation
- One-hot encoding with unknown-category handling

Classification evaluation:
- Accuracy
- F1-score
- Confusion matrix
- Most-frequent-class baseline

Regression evaluation:
- MAE in lakhs
- RMSE in lakhs
- R-squared
- Mean-prediction baseline
- Exact compound-growth formula baseline

Actual measured results:
reports/model_metrics.json

## Target Definitions
### Classification
The label is derived from a screening score:
- Price per sq ft at or below training city median: 2 points
- Parking: 1 point
- Security: 1 point
- Medium/high public transport accessibility: 1 point
- Ready-to-move status: 1 point

A score of at least 4 defines the positive label.
The classifier learns this rule-derived label.

Its probability output is uncalibrated and does not represent the
probability of earning an investment profit.

### Five-Year Regression
The synthetic target is:

    Future value = Current price * (1.06 ** 5)

Current price is an input. Therefore, regression scores measure
approximation of this formula, not accuracy on real future sales.
The exact formula is the preferred calculation for this scenario.

## Export All EDA Results
    .\.venv\Scripts\python.exe src/eda.py

Outputs:
- reports/eda/question_01.csv through question_20.csv
- reports/eda/findings.md

Question 10 is addressed using a cross-sectional comparison of
expensive localities. Historical price trends cannot be established
without dated price observations.

## Run the Website
    .\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502

Open:
http://127.0.0.1:8502

Keep this terminal running. Use a separate terminal for Git commands.

## Open MLflow
From the project folder, in another terminal:

    .\.venv\Scripts\python.exe -m mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

Open:
http://127.0.0.1:5000

Registered model names:
- EstateVision_investment_classifier
- EstateVision_future_value_regressor

If training completed but registration needs retrying:

    .\.venv\Scripts\python.exe src/register_models.py

Registration trusts only the explicitly listed types used by these
locally trained models.

## Architecture
    Source CSV
        -> Cleaning and feature engineering
        -> Processed housing dataset
        -> Training split and fitted preprocessing
        -> Classification and regression models
        -> Evaluation reports and MLflow
        -> Streamlit exploration and assessment interface

## Important Limitations
- Records are not verified current property advertisements.
- The source contains no observed future sale outcomes.
- Screening labels are defined criteria, not proven profitability.
- Growth scenarios exclude transaction costs, financing, taxes,
  maintenance, rental income, and inflation.
- Associations in EDA do not establish causal relationships.
- Crime rate, RERA, geographic coordinates, and dated sales history
  are not supplied as dataset columns.
- Global feature importance is not a causal or individual explanation.

## Source Files
- app.py: application and navigation
- src/visuals.py: cinematic homepage
- src/prepare_data.py: cleaning and feature engineering
- src/train_models.py: training, evaluation, and MLflow logging
- src/register_models.py: registration retry
- src/advisor.py: assessment form and model inference
- src/eda.py: 20 EDA analyses and exports
- models/metadata.json: model features and target definitions
- reports/: quality, evaluation, predictions, and EDA results

## GitHub
https://github.com/aayuabcd/estatevision-ai
