import logging
from llm.llm_client import LLMClient

logger = logging.getLogger(__name__)
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

def llm_judge(user_input: str, system_prompt: str):
    """사용자가 에이전트에서 빠져나가고자 하는 의사를 판단"""
    response = llm.chat_singleturn(
        user_input=user_input,
        system_prompt=system_prompt
    ).strip().upper()
    logger.info(f"[LLM JUDGE] 검색 중단 판단 결과: {response}")
    return response