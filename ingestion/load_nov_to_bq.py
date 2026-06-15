import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()
BQ_TABLE = f'{client.project}.ecommerce_raw.events'

print("Loading November data...")
df_nov_sample = pd.read_csv(
    'C:/churn-intelligence-platform/data/2019-Nov.csv',
    nrows=500_000
)

# Fix datetime column
df_nov_sample['event_time'] = pd.to_datetime(df_nov_sample['event_time'], utc=True)

# Fill missing string columns
df_nov_sample['category_code'] = df_nov_sample['category_code'].fillna('').astype(str)
df_nov_sample['brand'] = df_nov_sample['brand'].fillna('').astype(str)

print(f"November rows: {len(df_nov_sample)}")
print(df_nov_sample.dtypes)

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    autodetect=True,
)

job = client.load_table_from_dataframe(df_nov_sample, BQ_TABLE, job_config=job_config)
job.result()
print(f"Loaded {len(df_nov_sample)} November rows into BigQuery")