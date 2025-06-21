import os
from openai import OpenAI
from prompts.prompts import INTENT_CLASSIFIER
from config.config import get_config
from typing import Type
from pydantic import BaseModel

class OpenAIClient:
    def __init__(self, model_name: str):
        config = get_config()
        self.model_name = model_name
        self.client = OpenAI(api_key=config.get("OPENAI_API_KEY"))

    def classify_intent(self, user_message: str) -> str:
        prompt = INTENT_CLASSIFIER.format(user_message=user_message)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        return response.choices[0].message.content.strip().lower()
    
    def chat_singleturn(self, user_input: str, system_prompt: str = "") -> str:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    
    def chat_multiturn(self, user_input: str, system_prompt: str = "", chat_history: list = None) -> str:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if chat_history:
            for m in chat_history:
                if isinstance(m, dict) and "role" in m and "content" in m:
                    messages.append(m)
        # messages.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    
    def chat_multiturn_structured(self, response_format : Type[BaseModel], user_input: str, system_prompt: str = "", chat_history: list = None) -> BaseModel:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if chat_history:
            for m in chat_history:
                if isinstance(m, dict) and "role" in m and "content" in m:
                    messages.append(m)
        # messages.append({"role": "user", "content": user_input})
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=messages,
            response_format=response_format
        )
        return response.choices[0].message.parsed