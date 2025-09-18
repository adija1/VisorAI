-- Create a Redshift to Lambda integration so it can execute external Lambda funcrtion

CREATE or REPLACE EXTERNAL FUNCTION draft_customer_retail_review_emails(VARCHAR,VARCHAR,VARCHAR)
RETURNS VARCHAR(4000)
VOLATILE
LAMBDA 'function_name'
IAM_ROLE DEFAULT;

-- Run it 

SELECT customer, review, email,
       REPLACE(draft_customer_retail_review_emails(customer, review, email), '\n', ' ') AS draft_email_response
FROM "DB"."schema"."table"
WHERE
    customer = 'customer_name'
