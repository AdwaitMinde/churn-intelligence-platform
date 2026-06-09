import pandas as pd
import json
import time
from confluent_kafka import Producer

df = pd.read_csv('C:/churn-intelligence-platform/dev/sample.csv', nrows=5000)

# Kafka config
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(conf)

# Callback to confirm message delivery
def delivery_report(err, msg):
    if err is not None:
        print(f'Delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} partition [{msg.partition()}]')

# Load your sample CSV
df = pd.read_csv('C:/churn-intelligence-platform/dev/sample.csv')

print(f"Loaded {len(df)} rows. Starting to stream...")

# Stream row by row
for i, row in df.iterrows():
    message = {
        'event_time':  str(row['event_time']),
        'event_type':  str(row['event_type']),
        'product_id':  int(row['product_id']),
        'category_id': int(row['category_id']),
        'category_code': str(row.get('category_code', '')),
        'brand':       str(row.get('brand', '')),
        'price':       float(row['price']),
        'user_id':     int(row['user_id']),
        'user_session': str(row['user_session'])
    }

    # Publish to Kafka topic
    producer.produce(
        topic='ecommerce-events',
        key=str(row['user_id']),        # keyed by user_id so same user's events go to same partition
        value=json.dumps(message),
        callback=delivery_report
    )

    # Poll to trigger delivery callbacks
    producer.poll(0)

    # Throttle to simulate real-time (remove this later for full-speed ingestion)
    if i % 1000 == 0:
        print(f"Sent {i} messages...")
        time.sleep(0.5)

# Wait for all messages to be delivered before exiting
producer.flush()
print("All messages sent.")