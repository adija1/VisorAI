
-- Create the Redshift to Bedrock integration

CREATE EXTERNAL MODEL llm_claude
FUNCTION llm_claude_func
IAM_ROLE DEFAULT
MODEL_TYPE BEDROCK
SETTINGS (
   MODEL_ID '<model_id>')


-- Aggregation of reviews and sending them to Bedrock for sentiment analysis  
  
WITH aggregated_reviews AS (
    SELECT listagg(
        'Customer: ' || customer || ', Review: ' || review || '\n',
        ' '
    ) AS all_reviews
    FROM "DB"."schema"."table"
)
SELECT llm_claude_func(
    'Analyze the following customer reviews and provide a concise summary of the main reasons for negative feedback. Here are the reviews: ' 
    || all_reviews
    || ' Format your response in bullet points, keeping each point brief (under 10 words).'
) as negative_feedback_summary
FROM aggregated_reviews;


--  Perform classification as new columns

SELECT 
    customer, 
    review,
    llm_claude_func(
        'Perform a sentiment analysis on the following review: ' || review || 
        ' Provide just the sentiment (positive, negative, neutral or mixed) in one word. Nothing else '
    ) as sentiment,
    llm_claude_func(
        'For this review: ' || review || 
        ' Provide a brief, concise reason (10 words or less) for why this sentiment exists. Focus on the key factor.'
    ) as reason,
    llm_claude_func( 
'Classify this review into exactly one of these categories: support, delivery, cost. ' || 
'Review: ' || review || 
' Respond with just one word - either support, delivery, or cost. Base your classification on the main topic of the review.' 
) as category 
FROM "DB"."schema"."table"
order by customer
