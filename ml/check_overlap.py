from google.cloud import bigquery

client = bigquery.Client()
query = """
    WITH oct_buyers AS (
        SELECT DISTINCT user_id
        FROM `my-project-mail-422110.ecommerce_raw.events`
        WHERE event_type = 'purchase'
        AND DATE(event_time) BETWEEN '2019-10-01' AND '2019-10-31'
    ),
    nov_buyers AS (
        SELECT DISTINCT user_id
        FROM `my-project-mail-422110.ecommerce_raw.events`
        WHERE event_type = 'purchase'
        AND DATE(event_time) BETWEEN '2019-11-01' AND '2019-11-30'
    )
    SELECT
        COUNT(DISTINCT oct.user_id) as oct_buyers,
        COUNT(DISTINCT nov.user_id) as nov_buyers,
        COUNT(DISTINCT CASE WHEN nov.user_id IS NOT NULL THEN oct.user_id END) as retained,
        COUNT(DISTINCT CASE WHEN nov.user_id IS NULL THEN oct.user_id END) as churned
    FROM oct_buyers oct
    LEFT JOIN nov_buyers nov ON oct.user_id = nov.user_id
"""
for row in client.query(query).result():
    print(f"Oct buyers: {row[0]}, Nov buyers: {row[1]}, Retained: {row[2]}, Churned: {row[3]}")