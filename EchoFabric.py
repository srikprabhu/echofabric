from openai import AzureOpenAI
import json
import pandas as pd
import librosa

from config import OpenAIWhisperKEY
from config import OpenAIWhisperAPIVer
from config import OpenAIWhisperEndpoint
from config import OpenAIWhisperDeployment

from config import OpenAIChatKEY
from config import OpenAIChatAPIVer
from config import OpenAIChatEndpoint
from config import OpenAIChatModel

azure_openai_speech_client = AzureOpenAI(api_key=OpenAIWhisperKEY,
                                         api_version= OpenAIWhisperAPIVer,
                                         azure_endpoint = OpenAIWhisperEndpoint
                                         )

azure_openai_chat_client = AzureOpenAI(api_key = OpenAIChatKEY,
                                       api_version = OpenAIChatAPIVer,
                                       azure_endpoint = OpenAIChatEndpoint
                                       )


sample_query = """
Agent: Hello, thank you for calling XYZ Customer Support. My name is Alice. How can I assist you today?  
Customer: Hi Alice, my name is John Doe, and I have a major issue with my latest bill. I was overcharged by $50, and I don’t understand why.  
Agent: I’m sorry to hear that, John. Let me check your account. Could you provide me with your customer ID?  
Customer: Yes, it’s C123456.  
Agent: Thank you. I see that an additional charge was applied due to a late payment. However, I understand your concern. Would you like me to escalate this for a review?  
Customer: Yes, please. This is frustrating! I paid on time, and I shouldn’t be charged extra.  
Agent: I completely understand. I will escalate this issue to our billing team, and they will get back to you within 48 hours.  
Customer: Alright. Also, you guys really need to be more transparent with billing details. This is not the first time I’ve had to call about this.  
Agent: I appreciate your feedback, John. I have noted your concern. Is there anything else I can help you with?  
Customer: No, that’s all.  
Agent: Thank you for calling XYZ Customer Support. Have a great day!  

"""

sample_response = '{"Customer Name": "John Doe","Customer ID": "C123456", "Call Date & Time": "2025-02-11 14:30:00","Call Duration": "8 minutes","Agent Name": "Alice Smith", "Customer Sentiment": "Negative", "Is Abusive": "No", "Issue Category": "Billing", "Resolution Status": "Pending", "Escalation Required": "Yes", "Keywords Mentioned": ["Overcharged", "Billing error", "Late payment"],"Action Taken": "Agent escalated the issue to the billing team.", "Agent Response Quality": "Good", "Suggestion from Customer": "Improve billing transparency", "Customer Satisfaction Score": "Low", "Call Outcome": "Follow-up Required"}'


system_prompt = """

You are an advanced AI assistant that extracts structured information from transcribed customer call recordings. Given the call transcript below, analyze the conversation and extract key details in JSON format.

**Instructions:**
- Identify important details like sentiment, issue category, resolution status, etc.
- Ensure the output follows the structured key-value JSON format.
- If a value is unavailable, use `null`.

**Extracted Data (JSON Format):**  
Provide the structured output in the following format:
{
    "Customer Name": "<Extracted Name or null>",
    "Customer ID": "<Extracted ID or null>",
    "Agent Name": "<Extracted Agent Name or null>",
    "Customer Sentiment": "<Positive | Neutral | Negative>",
    "Is Abusive": "<Yes | No>",
    "Issue Category": "<Billing | Technical Issue | Cancellation | etc.>",
    "Resolution Status": "<Resolved | Not Resolved | Pending>",
    "Escalation Required": "<Yes | No>",
    "Keywords Mentioned": ["<keyword1>", "<keyword2>", ...],
    "Action Taken": "<Summary of agent’s action>",
    "Agent Response Quality": "<Good | Average | Poor>",
    "Suggestion from Customer": "<Extracted suggestion or null>",
    "Customer Satisfaction Score": "<High | Medium | Low>",
    "Call Outcome": "<Closed | Follow-up Required | Transferred>"
}

"""

def get_azure_openai_response_intent(client, prompt, query):
    try:
        response = client.chat.completions.create(
            model=OpenAIChatModel,temperature=0.3,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": sample_query},
                {"role": "assistant", "content": sample_response},
                {"role": "user", "content": query}
              ]
          )
        # return response
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Azure Open AI Error: Error\n {e}"
    

def get_call_insight(audio_test_file):
    transcription = azure_openai_speech_client.audio.transcriptions.create(
        file=audio_test_file,            
        model=OpenAIWhisperDeployment
    )

    print(transcription)#debugging

    call_insight = get_azure_openai_response_intent(azure_openai_chat_client, system_prompt, transcription.text)

    print(call_insight)#debugging

    insight=json.loads(call_insight)

    insight['Keywords Mentioned']=','.join(insight['Keywords Mentioned'])

    df=pd.DataFrame([insight])

    return df

# ##############TestScript############
if __name__ == "__main__":
    # file_path = r"C:\Users\sguchhait\Documents\Gen AI POC\EcoFabric\Mock Calls Collection\Mock Call #1_ (Telco Account) _Call Flow_ Account Verification. Billing. Offer. [ ezmp3.cc ].mp3"
    file_path=r"C:\Users\sguchhait\Documents\Gen AI POC\EcoFabric\audio_files_new\Speaker26_000.wav"
    audio_test_file=open(file_path, "rb")
    print(get_call_insight(audio_test_file))
