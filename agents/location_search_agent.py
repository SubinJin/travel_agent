import json
import re
from datetime import date
from typing import Dict
import logging
from langchain_core.tools import tool
from llm.llm_client import LLMClient
from prompts.prompts import JUDGE_RESERVATION_SYSTEM, LOCATION_SEARCH_SYSTEM_PROMPT
from common.forms import LocationSchema

logger = logging.getLogger(__name__)
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()


def extract_json_string(text: str) -> str:
    # ```json ~ ``` 제거
    cleaned = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return cleaned

@tool
def book_trip(slots: Dict[str, str]) -> str:
    """모든 장소 검색 정보를 바탕으로 mock 장소검색을 수행합니다."""
    return f"{slots.get('selected_place')}에 대한 상세 검색을 도와드릴게요. 궁금한 내용을 질문해주세요"


def llm_judges_cancel_intent(user_input: str) -> bool:
    system_prompt = JUDGE_RESERVATION_SYSTEM
    response = llm.chat_singleturn(user_input = user_input, system_prompt = system_prompt).strip().upper()
    logger.info(f"[장소검색] 예약 중단 판단 결과: {response}")
    return response == "YES"

def location_search_agent(state: dict) -> dict:
    slots = state.get("agent_state", {}).get("location_search", {})
    user_input = state.get("user_input", "")
    logger.info(f"[장소검색] 현재 사용자 발화: {user_input}")
    logger.info(f"[장소검색] 현재 슬롯 상태: {slots}")

    # LLM을 통한 장소검색 중단 판단
    # if llm_judges_cancel_intent(user_input):
    #     logger.info("[장소검색] LLM이 중단 판단")
    #     return {
    #         **state,
    #         "agent_response": "알겠습니다. 장소검색을 중단할게요.",
    #         "active_agent": None,
    #         "intent": None,
    #         "agent_state": {}  # 슬롯 초기화
    #     }
        
    system_prompt = LOCATION_SEARCH_SYSTEM_PROMPT.format(
        region = slots.get("region", ""),
        detail_level = slots.get("detail_level", ""),
        selected_place = slots.get("selected_place", ""),
        detail_search = slots.get("detail_search", ""),
        user_input = user_input,
        )
    logger.info(f"[장소검색] user_input : {user_input}")
    # llm_output = llm.chat_multiturn(system_prompt = system_prompt, user_input = user_input).strip()
    llm_output = llm.chat_multiturn_structured(system_prompt = system_prompt, user_input = user_input, response_format=LocationSchema)
    logger.info(f"[장소검색] LLM 응답: {llm_output}")
    
    try:
        # cleaned = extract_json_string(llm_output)
        # result = json.loads(cleaned)

        updated_slots = {
            "region": llm_output.region or slots.get("region", ""),
            "selected_place": llm_output.selected_place or slots.get("selected_place", ""),
            "detail_search": llm_output.detail_search or slots.get("detail_search", "")
        }
        message = llm_output.message

        # 2) detail_search 채워지면 종료
        if updated_slots.get("detail_search"):
            return {
                **state,
                "agent_response": message,
                "active_agent": "location_search_api",
                "intent": "location_search_api",
                "agent_state": {"location_search": slots},
                "user_input" : user_input
            }
        
        # 4. 누락 슬롯이 있다면 → LLM이 만든 멘트로 계속 유도
        return {
            **state,
            "agent_response": message,
            "agent_state": {"location_search": updated_slots},
            "active_agent": "location_search",
            "intent": "location_search"
        }

    except Exception as e:
        logger.warning(f"[장소검색] LLM 응답 파싱 실패: {e}")
        return {
            **state,
            "agent_response": "죄송합니다. 방금 내용을 잘 이해하지 못했어요. 다시 말씀해 주세요.",
            "agent_state": {
                **state.get("agent_state", {}),
                "reservation": slots
            },
            "active_agent": "reservation",
            "intent": "reservation"
        }

    
    
    