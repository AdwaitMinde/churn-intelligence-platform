import pandas as pd
import anthropic
from google.cloud import bigquery

bq_client = bigquery.Client()
claude = anthropic.Anthropic()

# Pull ALL churned customers (not just 20)
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
"""

print("Pulling all churned customers...")
df = bq_client.query(query).to_dataframe()
print(f"Loaded {len(df)} churned customers")

def build_prompt(row):
    return f"""You are a customer retention analyst. Based on the behavioral data below, write exactly 2 sentences explaining why this customer is at high risk of churning. Be specific to the numbers. No preamble.

Customer Profile:
- Days since last purchase: {int(row['recency_days'])}
- Total purchases: {int(row['frequency'])}
- Total spend: ${float(row['monetary']):.2f}
- Cart abandon rate: {float(row['cart_abandon_rate']):.0%}
- View-to-purchase ratio: {float(row['view_to_purchase_ratio']):.2%}
- Days active: {int(row['active_days'])}"""

# Generate explanations in batches
results = []
BATCH_SIZE = 50

for i, row in df.iterrows():
    try:
        response = claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{"role": "user", "content": build_prompt(row)}]
        )
        explanation = response.content[0].text.strip()
    except Exception as e:
        explanation = f"Explanation unavailable: {e}"

    results.append({
        "user_id":     int(row["user_id"]),
        "explanation": explanation
    })

    if (i + 1) % BATCH_SIZE == 0:
        print(f"Processed {i + 1}/{len(df)} customers...")

print(f"Generated {len(results)} explanations")

# Write to BigQuery
results_df = pd.DataFrame(results)

schema = [
    bigquery.SchemaField("user_id",     "INT64"),
    bigquery.SchemaField("explanation", "STRING"),
]

table_id = f"{bq_client.project}.ecommerce_marts.churn_explanations"
table    = bigquery.Table(table_id, schema=schema)
bq_client.create_table(table, exists_ok=True)

job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

job = bq_client.load_table_from_dataframe(results_df, table_id, job_config=job_config)
job.result()
print(f"Written {len(results_df)} explanations to BigQuery: {table_id}")