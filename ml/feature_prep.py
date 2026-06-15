import pandas as pd
from google.cloud import bigquery
from sklearn.model_selection import train_test_split

# Pull customer_features from BigQuery
client = bigquery.Client()

query = """
    SELECT
        user_id,
        recency_days,
        frequency,
        monetary,
        cart_abandon_rate,
        view_to_purchase_ratio,
        active_days,
        total_sessions,
        total_views,
        total_cart_adds,
        churned
    FROM `my-project-mail-422110.ecommerce_marts.customer_features`
    WHERE churned IS NOT NULL
"""

print("Pulling data from BigQuery...")
df = client.query(query).to_dataframe()
print(f"Loaded {len(df)} rows. Churn rate: {df['churned'].mean():.1%}")

# Features and label
FEATURES = [
    'recency_days', 'frequency', 'monetary',
    'cart_abandon_rate', 'view_to_purchase_ratio',
    'active_days', 'total_sessions', 'total_views', 'total_cart_adds'
]

X = df[FEATURES].fillna(0)
y = df['churned']

# Train/test split — stratified to preserve churn ratio
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
print(f"Train churn rate: {y_train.mean():.1%}, Test churn rate: {y_test.mean():.1%}")

# Save to CSV
X_train.to_csv('C:/churn-intelligence-platform/ml/X_train.csv', index=False)
X_test.to_csv('C:/churn-intelligence-platform/ml/X_test.csv', index=False)
y_train.to_csv('C:/churn-intelligence-platform/ml/y_train.csv', index=False)
y_test.to_csv('C:/churn-intelligence-platform/ml/y_test.csv', index=False)

print("Saved train/test splits to ml/")