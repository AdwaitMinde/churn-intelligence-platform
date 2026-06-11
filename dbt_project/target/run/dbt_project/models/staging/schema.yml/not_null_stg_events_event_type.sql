
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select event_type
from `my-project-mail-422110`.`ecommerce_marts`.`stg_events`
where event_type is null



  
  
      
    ) dbt_internal_test