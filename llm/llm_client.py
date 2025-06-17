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
    
    # def stream_chat(self, user_message: str):
    def stream_chat(self, messages: list[dict]):
        return self.client.stream_chat(messages)
    
    # def stream_chat(
    #     self,
    #     user_message: Optional[str] = None,
    #     messages: Optional[list[dict[str, str]]] = None
    # ):
    #     # 둘 다 없으면 오류
    #     if messages is None:
    #         if user_message is None:
    #             raise ValueError("user_message 또는 messages 중 하나는 반드시 제공해야 합니다.")
    #         messages = [{"role": "user", "content": user_message}]
    #     # OpenAIClient.stream_chat은 messages=... 만 처리하므로, 내부 client의 직접 호출
    #     return self.client.chat.completions.create(
    #         model=self.model_name,
    #         messages=messages,
    #         stream=True,
    #     )
    
    