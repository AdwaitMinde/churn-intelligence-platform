import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()
BQ_TABLE = f'{client.project}.ecommerce_raw.events'

# First delete the November data we already loaded
print("Removing existing November data...")
delete_query = """
    DELETE FROM `my-project-mail-422110.ecommerce_raw.events`
    WHERE DATE(event_time) >= '2019-11-01'
"""
client.query(delete_query).result()
print("Deleted existing November rows.")

# Load November in chunks, keep going until we have enough purchases
CHUNK_SIZE = 500_000
TARGET_PURCHASES = 50_000
total_purchases = 0
chunk_num = 0

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    autodetect=True,
)

print("Loading November data in chunks...")
for chunk in pd.read_csv(
    'C:/churn-intelligence-platform/data/2019-Nov.csv',
    chunksize=CHUNK_SIZE
):
    chunk['event_time'] = pd.to_datetime(chunk['event_time'], utc=True)
    chunk['category_code'] = chunk['category_code'].fillna('').astype(str)
    chunk['brand'] = chunk['brand'].fillna('').astype(str)

    job = client.load_table_from_dataframe(chunk, BQ_TABLE, job_config=job_config)
    job.result()

    chunk_purchases = (chunk['event_type'] == 'purchase').sum()
    total_purchases += chunk_purchases
    chunk_num += 1
    print(f"Chunk {chunk_num}: {len(chunk)} rows, {chunk_purchases} purchases. Total purchases so far: {total_purchases}")

    if total_purchases >= TARGET_PURCHASES:
        print(f"Reached {total_purchases} purchases. Stopping.")
        break

print("Done.")