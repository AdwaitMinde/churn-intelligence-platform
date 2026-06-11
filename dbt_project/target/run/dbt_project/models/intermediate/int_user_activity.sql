

  create or replace view `my-project-mail-422110`.`ecommerce_marts`.`int_user_activity`
  OPTIONS()
  as with events as (
    select * from `my-project-mail-422110`.`ecommerce_marts`.`stg_events`
),

user_activity as (
    select
        user_id,
        COUNT(*)                                                    as total_events,
        COUNTIF(event_type = 'view')                                as total_views,
        COUNTIF(event_type = 'cart')                                as total_cart_adds,
        COUNTIF(event_type = 'purchase')                            as total_purchases,
        SUM(case when event_type = 'purchase' then price else 0 end) as total_spend,
        MIN(event_time)                                             as first_event_time,
        MAX(event_time)                                             as last_event_time,
        COUNT(DISTINCT DATE(event_time))                            as active_days,
        COUNT(DISTINCT user_session)                                as total_sessions
    from events
    group by user_id
)

select * from user_activity;

