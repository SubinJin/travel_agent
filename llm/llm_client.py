from llm.openai.openai_client import OpenAIClient
from typing import Optional

class LLMClient:
    def __init__(self, service_name: str, model_name: str, **kwargs):
        self.service_name = service_name

        if service_name == "openai":
            self.client = OpenAIClient(model_name=model_name)

        else:
            raise ValueError(f"지원하지 않는 LLM 서비스: {service_name}")

    def get_client(self):
        return self.client
    
    def stream_chat(self, user_message: str):
        return self.client.stream_chat(user_message)
    
    