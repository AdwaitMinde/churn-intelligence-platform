

  create or replace view `my-project-mail-422110`.`ecommerce_marts`.`stg_events`
  OPTIONS()
  as with source as (
    select * from `my-project-mail-422110.ecommerce_raw.events`
),

renamed as (
    select
        TIMESTAMP(event_time)           as event_time,
        LOWER(TRIM(event_type))         as event_type,
        CAST(product_id as INT64)       as product_id,
        CAST(category_id as INT64)      as category_id,
        LOWER(TRIM(category_code))      as category_code,
        LOWER(TRIM(brand))              as brand,
        CAST(price as FLOAT64)          as price,
        CAST(user_id as INT64)          as user_id,
        TRIM(user_session)              as user_session
    from source
    where
        user_id is not null
        and event_time is not null
        and event_type in ('view', 'cart', 'purchase')
)

select * from renamed;

