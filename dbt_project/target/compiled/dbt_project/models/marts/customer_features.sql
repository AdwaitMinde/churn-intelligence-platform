with activity as (
    select * from `my-project-mail-422110`.`ecommerce_marts`.`int_user_activity`
),

events as (
    select * from `my-project-mail-422110`.`ecommerce_marts`.`stg_events`
),

-- October purchases per user
oct_purchases as (
    select
        user_id,
        COUNT(*) as oct_purchase_count
    from events
    where
        event_type = 'purchase'
        and DATE(event_time) between '2019-10-01' and '2019-10-31'
    group by user_id
),

-- November purchases per user
nov_purchases as (
    select
        user_id,
        COUNT(*) as nov_purchase_count
    from events
    where
        event_type = 'purchase'
        and DATE(event_time) between '2019-11-01' and '2019-11-30'
    group by user_id
),

final as (
    select
        a.user_id,

        -- RFM features
        DATE_DIFF(DATE('2019-11-30'), DATE(a.last_event_time), DAY)  as recency_days,
        a.total_purchases                                             as frequency,
        ROUND(a.total_spend, 2)                                       as monetary,

        -- Behavioral features
        ROUND(
            SAFE_DIVIDE(a.total_cart_adds - a.total_purchases, a.total_cart_adds), 4
        )                                                             as cart_abandon_rate,
        ROUND(
            SAFE_DIVIDE(a.total_purchases, a.total_views), 6
        )                                                             as view_to_purchase_ratio,
        a.active_days,
        a.total_sessions,
        a.total_views,
        a.total_cart_adds,

        -- Churn label
        -- Churned = bought in October but NOT in November
        case
            when oct_purchases.oct_purchase_count > 0
                 and nov_purchases.nov_purchase_count is null then 1
            when oct_purchases.oct_purchase_count > 0
                 and nov_purchases.nov_purchase_count > 0 then 0
            else null  -- exclude users with no October purchases
        end as churned

    from activity a
    left join oct_purchases on a.user_id = oct_purchases.user_id
    left join nov_purchases on a.user_id = nov_purchases.user_id
)

select * from final
where churned is not null  -- only keep labeled users