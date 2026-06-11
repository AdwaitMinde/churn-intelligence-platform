
    
    

with all_values as (

    select
        event_type as value_field,
        count(*) as n_records

    from `my-project-mail-422110`.`ecommerce_marts`.`stg_events`
    group by event_type

)

select *
from all_values
where value_field not in (
    'view','cart','purchase'
)


