from google.cloud import bigquery

client = bigquery.Client()
query = """
    SELECT
        risk_tier,
        churned,
        COUNT(*) as customers,
        ROUND(AVG(recency_days), 1) as avg_recency,
        ROUND(AVG(monetary), 2) as avg_spend,
        COUNTIF(explanation IS NOT NULL) as has_explanation
    FROM `my-project-mail-422110.ecommerce_marts.churn_dashboard_view`
    GROUP BY risk_tier, churned
    ORDER BY risk_tier, churned
"""
for row in client.query(query).result():
    print(f"Risk: {row[0]:8} | Churned: {row[1]} | Customers: {row[2]:5} | Avg recency: {row[3]:5} days | Avg spend: ${row[4]:8.2f} | Has explanation: {row[5]}")