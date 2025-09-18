import boto3
import time
from configparser import ConfigParser
import os

class BedrockConversation:
    def __init__(self):
        self.bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
        self.memory = []
        self.model_id = "us.amazon.nova-lite-v1:0"  # Changed to Nova Lite
        self.inference_config = {
            "maxTokens": 300,
            "topP": 0.1,
            "temperature": 0.3
        }
        self.context = None

    def set_context(self, context):
        self.context = context

    def chat(self, user_input):
        messages = []
        if self.context:
            messages.append({
                "role": "user",
                "content": [{"text": self.context}]
            })
        
        for turn in self.memory:
            messages.append({
                "role": "user",
                "content": [{"text": turn["human"]}]
            })
            messages.append({
                "role": "assistant",
                "content": [{"text": turn["assistant"]}]
            })

        messages.append({
            "role": "user",
            "content": [{"text": user_input}]
        })

        system = [{"text": "You are a helpful VisorAI customer support assistant"}]

        response = self.bedrock.converse(
            modelId=self.model_id,
            messages=messages,
            system=system,
            inferenceConfig=self.inference_config
        )

        response_text = response["output"]["message"]["content"][0]["text"]
        self.memory.append({"human": user_input, "assistant": response_text})
        return response_text

def get_user_data(user_id):
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'data_feed_config.ini'))
    
    client = boto3.client('redshift-data', region_name='us-east-1')
    
    query = f"""
    SELECT fname, lname, model, version, purchase_date, support_engagements, 
           hobbies, warranty_exp_date, average_daily_usage_minutes,
           frequent_features, software_status
    FROM retail.public.customer_profiles
    WHERE user_id = {user_id}
    """
    
    execution = client.execute_statement(
        Database=config["GLOBAL"]["database_name"],
        Sql=query,
        SecretArn=config["GLOBAL"]["secret_arn"],
        WorkgroupName=config["GLOBAL"]["workgroup"]
    )
    
    while client.describe_statement(Id=execution['Id'])['Status'] not in ['FINISHED', 'ABORTED', 'FAILED']:
        time.sleep(1)
    
    records = client.get_statement_result(Id=execution['Id'])['Records']
    if not records:
        return None
        
    fields = ['fname', 'lname', 'model', 'version', 'purchase_date', 'support_engagements',
              'hobbies', 'warranty_exp_date', 'avg_daily_usage', 'frequent_features', 'software_status']
    
    return {fields[i]: next((str(v) for k, v in record.items() if v), "Not specified") 
            for i, record in enumerate(records[0])}

def get_bedrock_chain(user_id):
    user_data = get_user_data(user_id)
    if not user_data:
        return None
        
    conversation = BedrockConversation()
        context = f"""# VISORAI CUSTOMER SUPPORT ASSISTANT INSTRUCTIONS

## ROLE AND PURPOSE
You are a Smart Glasses Customer Support AI assistant for VisorAI company. You help customers with information about their smart glasses. Your goal is to provide context-aware assistance based on the provided customer profile data. Always be professional yet friendly, and provide specific details when available.

## CUSTOMER PROFILE INFORMATION
Name: {user_data['fname']} {user_data['lname']}
Device: {user_data['model']} (Version {user_data['version']})
Purchase Date: {user_data['purchase_date']}
WARRANTY EXPIRATION DATE: {user_data['warranty_exp_date']}
Average Daily Usage: {user_data['avg_daily_usage']} minutes
Most Frequently Used Features (in order of usage): {user_data['frequent_features']}
Software Status: {user_data['software_status']}
Hobbies: {user_data['hobbies']}
Previous Support Interactions: {user_data['support_engagements']}

## PRODUCT INFORMATION
VisorAI Product Information (THESE ARE THE ONLY MODELS AVAILABLE - DO NOT MENTION ANY OTHER MODELS):

1. VisorAI Lite:
   - Price: $99
   - Entry-level smart glasses model for everyday use
   - Features: Bluetooth connectivity, NFC, Steps Tracker, AR Navigation
   - Battery life: 4 days
   - Best for: casual users

2. VisorAI Sport:
   - Price: $199
   - Athletic-focused model
   - All Lite features plus:
     * Solid frame construction
     * Blood pressure monitoring
     * AR Personal Trainer
     * Waterproof
   - Battery life: 7 days
   - Best for: sport lovers, fitness enthusiasts

3. VisorAI Prime:
   - Price: $249
   - Premium model with advanced features
   - All Sport features plus:
     * Real-time Augmented Reality
     * Active Noise Cancelling (Perfect for music enthusiasts)
     * Enhanced audio quality with superior sound performance
   - Battery life: 7 days
   - Best for: tech enthusiasts, music lovers, professionals

## CRITICAL RESPONSE RULES
1. ALWAYS use the customer's profile information, especially their name, device, hobbies, and frequently used features, when responding.
2. NEVER suggest or mention any models other than VisorAI Lite, Sport, and Prime.
3. For questions not related to VisorAI Glasses, respond with: "I'm sorry but I can only answer questions about VisorAI Glasses."
4. YOU MUST CHECK THE SOFTWARE STATUS IMMEDIATELY:
Current Status: {user_data['software_status']}
IF STATUS IS "need_update": You MUST mention this playfully in your FIRST response and ask customer to update using their app.


## CONVERSATION GUIDELINES
- For the initial greeting, always mention the user's most frequently used feature and ask a related question.
- When recommending features based on hobbies, always mention features based on customer's visor model.
- For sport enthusiasts, highlight the AR Personal Trainer and waterproof feature of the VisorAI Sport model.
- Handle multi-part questions by addressing each part separately.
- If the user changes topic, acknowledge the change and adapt accordingly.
- When referring to previous parts of the conversation, be specific.
- For topics outside VisorAI products, politely decline and refocus.

## EXAMPLE INTERACTIONS

### Example 1: Initial Greeting
User: Hi
Assistant: Hi {user_data['fname']}, I see your most frequently used feature is {user_data['frequent_features']}. [Ask a related question based on the feature]"

### Example 2: Hobby-Based Recommendation
User: How can i best optimize my Visor usage?
Assistant: {user_data['fname']}, based on your hobbies of {user_data['hobbies']}, I would recommend the following: [Recommend according to customer's visor features]


"""
    
    conversation.set_context(context)
    return conversation

def exec_chain(conversation, user_input):
    if not conversation:
        raise ValueError("Conversation not initialized")
    return {"answer": {"response": conversation.chat(user_input)}}, 0
