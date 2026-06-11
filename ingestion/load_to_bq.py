import boto3
import json
from google.cloud import bigquery
from datetime import datetime
import tempfile
import os

# Clients
s3_client = boto3.client('s3')
bq_client  = bigquery.Client()

# Config
S3_BUCKET = 'churn-platform-raw-events-adwait'
S3_PREFIX = 'raw/events/'
BQ_TABLE  = f'{bq_client.project}.ecommerce_raw.events'

# Schema
schema = [
    bigquery.SchemaField('event_time',    'TIMESTAMP'),
    bigquery.SchemaField('event_type',    'STRING'),
    bigquery.SchemaField('product_id',    'INT64'),
    bigquery.SchemaField('category_id',   'INT64'),
    bigquery.SchemaField('category_code', 'STRING'),
    bigquery.SchemaField('brand',         'STRING'),
    bigquery.SchemaField('price',         'FLOAT64'),
    bigquery.SchemaField('user_id',       'INT64'),
    bigquery.SchemaField('user_session',  'STRING'),
]

# Create table if it doesn't exist
table = bigquery.Table(BQ_TABLE, schema=schema)
table = bq_client.create_table(table, exists_ok=True)
print(f"Table ready: {BQ_TABLE}")

# Job config — bulk load, append to table
job_config = bigquery.LoadJobConfig(
    schema=schema,
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
)

# List all batch files in S3
paginator = s3_client.get_paginator('list_objects_v2')
pages     = paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_PREFIX)

all_keys = []
for page in pages:
    for obj in page.get('Contents', []):
        all_keys.append(obj['Key'])

print(f"Found {len(all_keys)} files in S3. Starting load...")

# Process in chunks of 50 files at a time
CHUNK_SIZE = 50
rows_total = 0

for chunk_start in range(0, len(all_keys), CHUNK_SIZE):
    chunk = all_keys[chunk_start:chunk_start + CHUNK_SIZE]

    # Combine chunk into one temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        for key in chunk:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
            content  = response['Body'].read().decode('utf-8')
            tmp.write(content + '\n')
        tmp_path = tmp.name

    # Load temp file into BigQuery
    with open(tmp_path, 'rb') as f:
        load_job = bq_client.load_table_from_file(f, BQ_TABLE, job_config=job_config)
        load_job.result()  # wait for job to complete

    os.unlink(tmp_path)  # delete temp file

    rows_total += CHUNK_SIZE * 1000
    print(f"Loaded files {chunk_start+1}–{chunk_start+len(chunk)} of {len(all_keys)}")

print(f"\nDone. Verifying row count...")

# Verify
query = f"SELECT COUNT(*) as total FROM `{BQ_TABLE}`"
result = bq_client.query(query).result()
for row in result:
    print(f"Total rows in BigQuery: {row.total}")