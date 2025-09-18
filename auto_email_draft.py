import json
import boto3
from datetime import datetime

# Define boto3 clients for Amazon Bedrock invocation and Amazon SES
bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
ses_client = boto3.client('ses', region_name='us-east-1')

# Define parameters for the Nova model invocation
NOVA_MODEL_ID = "us.amazon.nova-lite-v1:0"

def call_nova_llm(customer, review):
    system_list = [
        {
            "text": "You are an empathetic customer service representative for VisorAI, drafting personalized email responses to customer reviews of VisorAI Smart Glasses. Your responses should be ready to send, with no signatures or closing elements."
        }
    ]

    message_list = [
        {
            "role": "user",
            "content": [
                {
                    "text": f"""Draft a detailed and empathetic follow-up email to {customer} based on their recent review of their VisorAI Smart Glasses. This email will be sent directly to the customer, so ensure it's complete and ready to send. Follow these guidelines:

1. Start with 'Dear [Customer's first name],'
2. If the review is negative:
   - Express sincere apologies for their experience
   - Acknowledge specific issues mentioned in their review.
   - offer our brand new rechargable case free of charge.
3. Limit the response to 150-200 words for conciseness while maintaining detail
4. End the email with 'We wish you a smart and clear day!'
5. Do not include any signatures, closing phrases, or additional elements after 'We wish you a smart and clear day!'

Here is the review: {review}

Remember to maintain a warm, professional tone throughout the email and ensure it's ready to be sent as-is, ending with 'We wish you a smart and clear day!'"""
                }
            ]
        }
    ]

    

    inf_params = {"max_new_tokens": 500, "top_p": 0.9, "top_k": 20, "temperature": 0.7}

    request_body = {
        "schemaVersion": "messages-v1",
        "messages": message_list,
        "system": system_list,
        "inferenceConfig": inf_params,
    }

    response = bedrock_client.invoke_model_with_response_stream(
        modelId=NOVA_MODEL_ID,
        body=json.dumps(request_body)
    )

    full_text = ""
    stream = response.get("body")
    if stream:
        for event in stream:
            chunk = event.get("chunk")
            if chunk:
                chunk_json = json.loads(chunk.get("bytes").decode())
                content_block_delta = chunk_json.get("contentBlockDelta")
                if content_block_delta:
                    full_text += content_block_delta.get("delta").get("text", "")

    return full_text

# Function to send email using Amazon SES
def send_email(email_address, subject, body):
    signature = "\n\nVisorAI Customer Experience Team"
    full_body = body + signature
    
    response = ses_client.send_email(
        Source='visorai@mail.com',  # Replace with your "From" address
        Destination={'ToAddresses': [email_address]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': full_body}}
        }
    )
    return response

# Main Lambda handler
def lambda_handler(event, context):
    try:
        records = event["arguments"]
        results = []
        for record in records:
            customer = record[0]
            review = record[1]
            email_address = record[2]
            try:
                email_content = call_nova_llm(customer, review)
                results.append(email_content)
                send_email(email_address, "Follow-up on Your VisorAI Smart Glasses Review", email_content)
            except Exception as e:
                results.append(str(e))
        response = {'success': True, 'results': results}
    except Exception as e:
        response = {'success': False, 'error_msg': str(e)}
    return json.dumps(response)
