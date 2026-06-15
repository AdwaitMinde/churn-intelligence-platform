from google.cloud import bigquery

client = bigquery.Client()
query = """
    SELECT
        event_type,
        DATE(event_time) as event_date,
        COUNT(*) as cnt
    FROM `my-project-mail-422110.ecommerce_raw.events`
    WHERE DATE(event_time) >= '2019-11-01'
    GROUP BY event_type, event_date
    ORDER BY event_date, event_type
"""
for row in client.query(query).result():
    print(row)