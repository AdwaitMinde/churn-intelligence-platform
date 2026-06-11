
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select churned
from `my-project-mail-422110`.`ecommerce_marts`.`customer_features`
where churned is null



  
  
      
    ) dbt_internal_test