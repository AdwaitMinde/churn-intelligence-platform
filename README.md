# Real-Time Customer Churn Intelligence Platform

An end-to-end data platform that streams e-commerce events through Kafka, transforms them in BigQuery via dbt, predicts customer churn with XGBoost, and generates plain-English explanations for each at-risk customer using Claude AI.

---

## Architecture
            Kaggle Dataset (285M events)

                            ↓

    Kafka Producer → Kafka Topic → Kafka Consumer

                            ↓

                        AWS S3

                            ↓

                        BigQuery (raw)

                             ↓

                    dbt (staging → marts)

                              ↓

            ┌─────────────────┴──────────────────┐

            ↓                                    ↓

     XGBoost Model                       Claude AI (Haiku)

    (churn prediction)                  (explanation generation)

            ↓                                    ↓

            └─────────────────┬──────────────────┘

                              ↓

                churn_dashboard_view (BigQuery)

                            ↓

                    Streamlit Dashboard

---

## Key Results

| Metric | Value |
|---|---|
| Events processed | 500,000 |
| Labeled customers | 7,362 |
| XGBoost AUC | 0.9956 |
| XGBoost F1 | 0.9911 |
| LLM explanations generated | 6,826 |
| Overall churn rate | 92.7% |
| Top churn predictor | Recency (days since last purchase) |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Streaming | Apache Kafka (Docker) |
| Storage | AWS S3 |
| Data Warehouse | Google BigQuery |
| Transformation | dbt |
| ML Model | XGBoost + MLflow |
| Explainability | SHAP |
| LLM Layer | Anthropic Claude Haiku |
| Dashboard | Streamlit + Plotly |
| Language | Python 3.12 |

---

## Project Structure
churn-intelligence-platform/

├── ingestion/          # Kafka producer, consumer, S3→BigQuery loaders

├── dbt_project/        # dbt models (staging, intermediate, marts)

│   └── models/

│       ├── staging/        # stg_events

│       ├── intermediate/   # int_user_activity

│       └── marts/          # customer_features, churn_dashboard_view

├── ml/                 # Feature prep, training, SHAP, LLM explanations

├── dashboard/          # Streamlit app

└── docker-compose.yml  # Kafka + Zookeeper

---

## Pipeline Walkthrough

**1. Ingestion** — A Kafka producer streams 500K e-commerce events (views, cart adds, purchases) row by row from the REES46 Kaggle dataset. A Kafka consumer batches these into newline-delimited JSON files and lands them in S3.

**2. Warehousing** — Raw JSON files are bulk-loaded into BigQuery. dbt models clean and transform the data into a `customer_features` mart with RFM features, behavioral metrics, and a churn label (purchased in October but not November = churned).

**3. ML Pipeline** — XGBoost trains on 9 behavioral features with `scale_pos_weight` to handle class imbalance. Three experiments are tracked in MLflow. The best model (AUC 0.9956) is registered in the MLflow Model Registry. SHAP analysis identifies recency and frequency as the top churn drivers.

**4. LLM Explanation Layer** — For each of the 6,826 churned customers, Claude Haiku generates a 2-sentence plain-English explanation grounded in their specific behavioral data. Explanations are written back to BigQuery.

**5. Dashboard** — A Streamlit app queries the final `churn_dashboard_view` (features + predictions + explanations) and renders an analyst-facing explorer and an executive summary with Plotly charts.

---

## How to Run Locally

### Prerequisites
- Docker Desktop
- Python 3.10+
- AWS account (free tier)
- GCP account (free tier BigQuery)
- Anthropic API key

### Setup

```bash
# Clone the repo
git clone https://github.com/AdwaitMinde/churn-intelligence-platform.git
cd churn-intelligence-platform

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Start Kafka
docker-compose up -d

# Set environment variables
$env:GOOGLE_APPLICATION_CREDENTIALS = "config/gcp-credentials.json"
$env:ANTHROPIC_API_KEY = "your-key-here"
```

### Run the pipeline

```bash
# 1. Stream events to S3
python ingestion/producer.py   # Terminal 1
python ingestion/consumer.py   # Terminal 2

# 2. Load to BigQuery
python ingestion/reload_all_events.py

# 3. Transform with dbt
cd dbt_project && dbt run && dbt test

# 4. Train model
python ml/feature_prep.py
python ml/train.py

# 5. Generate LLM explanations
python ml/write_explanations_to_bq.py

# 6. Launch dashboard
streamlit run dashboard/app.py
```

---

## Data Source

[REES46 eCommerce Behavior Data](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store) — 285M behavioral events from a real multi-category e-commerce store.

---

## Key Design Decisions

**Why XGBoost over deep learning?** Tabular churn data with engineered RFM features is a classic XGBoost use case. It trains fast, is interpretable via SHAP, and outperforms neural networks on structured data at this scale.

**Why Claude for explanations?** Rule-based explanations would be brittle and require constant maintenance. An LLM generates nuanced, customer-specific explanations that are immediately usable by retention teams without further processing.

**Why dbt for transformation?** dbt enforces SQL-based transformation with version control, schema tests, and lineage tracking — the same pattern used in production data teams at scale.