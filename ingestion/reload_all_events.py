import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()
BQ_TABLE = f'{client.project}.ecommerce_raw.events'

job_config_truncate = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    autodetect=True,
)
job_config_append = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    autodetect=True,
)

def load_chunk(df, config):
    df['event_time'] = pd.to_datetime(df['event_time'], utc=True)
    df['category_code'] = df['category_code'].fillna('').astype(str)
    df['brand'] = df['brand'].fillna('').astype(str)
    job = client.load_table_from_dataframe(df, BQ_TABLE, job_config=config)
    job.result()

# Step 1 — reload October (truncate first)
print("Loading October data (truncating table)...")
oct_chunk = pd.read_csv(
    'C:/churn-intelligence-platform/data/2019-Oct.csv',
    nrows=500_000
)
load_chunk(oct_chunk, job_config_truncate)
print(f"Loaded {len(oct_chunk)} October rows.")

# Step 2 — append November chunks until 50K purchases
TARGET_PURCHASES = 50_000
total_purchases = 0
chunk_num = 0

print("Appending November data...")
for chunk in pd.read_csv(
    'C:/churn-intelligence-platform/data/2019-Nov.csv',
    chunksize=500_000
):
    load_chunk(chunk, job_config_append)
    chunk_purchases = (chunk['event_type'] == 'purchase').sum()
    total_purchases += chunk_purchases
    chunk_num += 1
    print(f"Chunk {chunk_num}: {len(chunk)} rows, {chunk_purchases} purchases. Total: {total_purchases}")

    if total_purchases >= TARGET_PURCHASES:
        print(f"Reached {total_purchases} purchases. Stopping.")
        break

print("Done. Run dbt next.")