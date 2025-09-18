# The following is a code repository & information about the VisorAI presentation by Liat & Adi

The VisorAI presentation is an engaging presentation about a fake company called "VisorAI" that manufactures AI Powered Smart Glasses. 
The presentation, comprised of 6 live demos, takes you on a journey from the perspective of VisorAI customers, managers, analysts and AI engineers. 

## Demo 1 - Chatbot
When the customer logs in to the chatbot (Streamlit app) the chatbot extracts the relevant information from Redshift, builds a customer profile and send that as an enriched prompt to Amazon Bedrock. 
The logic can be found in AdVisor_Chatbot.py
The UI file is missing but you can use any IDE these days to generate a streamlit app that will use the code in the Chatbot file.

## Demo 2 - Quicksight Q 
Our data is our data but you can experiment with Quicksit Q here
https://democentral.learnquicksight.online/#QCustom-AskQ-Q-More-Ways-To-Q

## Demo 3 - Scenarios (Deep Analysis)
Read all about it here - https://aws.amazon.com/quicksight/q/scenarios/

## Demo 4 - Feedback analysis on Redshift 
Checkout redshift_bedrock.sql to use the native integration between Amazon Redshift & Amazon Bedrock

## Demo 5 - Automatic email draft
Look at redshift_lambda_auto_email.sql for the Redshift part & auto_email_draft.py for the Lambda function

## Demo 6 - Video Game Analyst (using AgentCore & Strands)
Here it is
https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/02-use-cases/video-games-sales-assistant

