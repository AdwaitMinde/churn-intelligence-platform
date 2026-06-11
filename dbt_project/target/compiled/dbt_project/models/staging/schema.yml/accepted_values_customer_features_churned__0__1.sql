
    
    

with all_values as (

    select
        churned as value_field,
        count(*) as n_records

    from `my-project-mail-422110`.`ecommerce_marts`.`customer_features`
    group by churned

)

select *
from all_values
where value_field not in (
    '0','1'
)


