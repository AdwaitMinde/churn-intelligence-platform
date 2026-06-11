
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select user_id
from `my-project-mail-422110`.`ecommerce_marts`.`customer_features`
where user_id is null



  
  
      
    ) dbt_internal_test