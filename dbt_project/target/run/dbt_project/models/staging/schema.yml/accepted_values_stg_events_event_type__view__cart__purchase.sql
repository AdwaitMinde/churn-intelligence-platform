
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

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



  
  
      
    ) dbt_internal_test