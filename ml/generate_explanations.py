import pandas as pd
import anthropic
from google.cloud import bigquery

# Clients
bq_client = bigquery.Client()
claude = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

# Pull high-risk customers from BigQuery
query = """
    SELECT
        user_id,
        recency_days,
        frequency,
        monetary,
        cart_abandon_rate,
        view_to_purchase_ratio,
        active_days
    FROM `my-project-mail-422110.ecommerce_marts.customer_features`
    WHERE churned = 1
    LIMIT 20
"""

print("Pulling high-risk customers from BigQuery...")
df = bq_client.query(query).to_dataframe()
print(f"Loaded {len(df)} customers")

def build_prompt(row):
    return f"""You are a customer retention analyst. Based on the behavioral data below, write exactly 2 sentences explaining why this customer is at high risk of churning. Be specific to the numbers. No preamble.

Customer Profile:
- Days since last purchase: {int(row['recency_days'])}
- Total purchases: {int(row['frequency'])}
- Total spend: ${float(row['monetary']):.2f}
- Cart abandon rate: {float(row['cart_abandon_rate']):.0%}
- View-to-purchase ratio: {float(row['view_to_purchase_ratio']):.2%}
- Days active: {int(row['active_days'])}"""

# Generate explanations
results = []
for i, row in df.iterrows():
    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": build_prompt(row)}]
    )
    explanation = response.content[0].text.strip()
    results.append({
        "user_id":     row["user_id"],
        "explanation": explanation
    })
    print(f"[{i+1}/{len(df)}] User {row['user_id']}: {explanation[:80]}...")

# Save locally to review
results_df = pd.DataFrame(results)
results_df.to_csv('C:/churn-intelligence-platform/ml/sample_explanations.csv', index=False)
print(f"\nDone. Saved to ml/sample_explanations.csv")
print("\nSample output:")
print(results_df[['user_id', 'explanation']].head(3).to_string(index=False))