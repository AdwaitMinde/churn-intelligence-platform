with features as (
    select * from {{ ref('customer_features') }}
),

explanations as (
    select * from `my-project-mail-422110.ecommerce_marts.churn_explanations`
),

final as (
    select
        f.user_id,
        f.recency_days,
        f.frequency,
        f.monetary,
        f.cart_abandon_rate,
        f.view_to_purchase_ratio,
        f.active_days,
        f.total_sessions,
        f.total_views,
        f.total_cart_adds,
        f.churned,

        -- Risk tier based on recency and frequency
        case
            when f.recency_days > 45 and f.frequency = 1 then 'High'
            when f.recency_days > 30 and f.frequency <= 2 then 'Medium'
            else 'Low'
        end as risk_tier,

        e.explanation

    from features f
    left join explanations e on f.user_id = e.user_id
)

select * from final