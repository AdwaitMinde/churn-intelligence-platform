import json
import boto3
from datetime import datetime
from confluent_kafka import Consumer, KafkaException

# Kafka config
kafka_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'churn-pipeline-consumer',
    'auto.offset.reset': 'earliest'   # start from beginning if no offset stored
}

consumer = Consumer(kafka_conf)
consumer.subscribe(['ecommerce-events'])

# S3 config
S3_BUCKET = 'churn-platform-raw-events-adwait'   # replace with your bucket name
s3_client = boto3.client('s3')

BATCH_SIZE = 1000
batch = []
batch_count = 0

def write_batch_to_s3(batch, batch_count):
    now = datetime.utcnow()
    # Organise files by date so they're easy to query later
    s3_key = f"raw/events/{now.strftime('%Y/%m/%d')}/batch_{batch_count}_{now.strftime('%H%M%S')}.json"

    # Each line is one JSON object (newline-delimited JSON — BigQuery loves this format)
    payload = '\n'.join(json.dumps(record) for record in batch)

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=payload.encode('utf-8')
    )
    print(f"Written batch {batch_count} ({len(batch)} records) → s3://{S3_BUCKET}/{s3_key}")

print("Consumer started. Waiting for messages...")

try:
    while True:
        msg = consumer.poll(timeout=5.0)   # wait up to 5 seconds for a message

        if msg is None:
            # No message in the last 5 seconds
            if batch:
                # Flush whatever is left in the batch
                write_batch_to_s3(batch, batch_count)
                batch_count += 1
                batch = []
            print("No new messages. Waiting...")
            continue

        if msg.error():
            raise KafkaException(msg.error())

        # Deserialize the message
        record = json.loads(msg.value().decode('utf-8'))
        batch.append(record)

        # Write to S3 when batch is full
        if len(batch) >= BATCH_SIZE:
            write_batch_to_s3(batch, batch_count)
            batch_count += 1
            batch = []

except KeyboardInterrupt:
    # Ctrl+C pressed — flush remaining batch before exiting
    print("Shutting down...")
    if batch:
        write_batch_to_s3(batch, batch_count)

finally:
    consumer.close()
    print(f"Done. Total batches written: {batch_count}")