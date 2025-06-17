import os
from openai import OpenAI
from prompts.prompts import INTENT_CLASSIFIER
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def classify_intent(self, user_message: str) -> str:
        prompt = INTENT_CLASSIFIER.format(user_message=user_message)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        return response.choices[0].message.content.strip().lower()
    
    # def stream_chat(self, user_input: str):
    #     return self.client.chat.completions.create(
    #         model=self.model_name,
    #         messages=[{"role": "user", "content": user_input}],
    #         stream=True,
    #     )
        
    def stream_chat(self, messages: list[dict]):
        """
        messages: List of {"role": "user"|"assistant", "content": "..."} 
        containing full history  새로운 user 입력
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
        )
    
    def chat(self, user_input: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": user_input}],
            temperature=0,
        )
        return response.choices[0].message.content.strip()