import json
import re
from datetime import date
from typing import Dict
import logging
from langchain_core.tools import tool
from llm.llm_client import LLMClient
from prompts.prompts import JUDGE_RESERVATION_SYSTEM, RESERVATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
REQUIRED_SLOTS = ["departure", "arrival", "start_date", "end_date"]
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()


def extract_json_string(text: str) -> str:
    # ```json ~ ``` 제거
    cleaned = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return cleaned

@tool
def book_trip(slots: Dict[str, str]) -> str:
    """모든 예약 정보를 바탕으로 mock 예약을 수행합니다."""
    return (
        f"{slots['departure']}에서 {slots['arrival']}까지 "
        f"{slots['start_date']} ~ {slots['end_date']} 여행이 예약되었습니다!"
    )

def llm_judges_cancel_intent(user_input: str) -> bool:
    system_prompt = JUDGE_RESERVATION_SYSTEM
    response = llm.chat_singleturn(user_input = user_input, system_prompt = system_prompt).strip().upper()
    logger.info(f"[예약] 예약 중단 판단 결과: {response}")
    return response == "YES"

def fill_slots(state: dict) -> dict:
    slots = state.get("agent_state", {}).get("reservation", {})
    user_input = state.get("user_input", "")
    logger.info(f"[예약] 현재 사용자 발화: {user_input}")
    logger.info(f"[예약] 현재 슬롯 상태: {slots}")

    # LLM을 통한 예약 중단 판단
    if llm_judges_cancel_intent(user_input):
        logger.info("[예약] LLM이 중단 판단")
        return {
            **state,
            "agent_response": "알겠습니다. 예약을 중단할게요.",
            "active_agent": None,
            "intent": None,
            "agent_state": {}  # 슬롯 초기화
        }
        
    system_prompt = RESERVATION_SYSTEM_PROMPT.format(
        departure = slots.get("departure", ""),
        arrival = slots.get("arrival", ""),
        start_date = slots.get("start_date", ""),
        end_date = slots.get("end_date", ""),
        user_input = user_input,
        today = date.today())
    logger.info(f"[예약] user_input : {user_input}")
    llm_output = llm.chat_multiturn(system_prompt = system_prompt, user_input = user_input).strip()
    logger.info(f"[예약] LLM 응답: {llm_output}")
    
    try:
        cleaned = extract_json_string(llm_output)
        result = json.loads(cleaned)

        updated_slots = {
            "departure": result.get("departure") or slots.get("departure", ""),
            "arrival": result.get("arrival") or slots.get("arrival", ""),
            "start_date": result.get("start_date") or slots.get("start_date", ""),
            "end_date": result.get("end_date") or slots.get("end_date", ""),
        }
        message = result.get("message", "죄송합니다. 응답을 생성하지 못했습니다.")

        # 3. 슬롯이 모두 채워졌다면 → 예약 완료
        missing = [k for k in REQUIRED_SLOTS if not updated_slots.get(k)]
        logger.info(f"[예약] 누락 슬롯: {missing}")

        if not missing:
            # response = book_trip(slots = updated_slots)
            response = book_trip.invoke({"slots": updated_slots})
            return {
                **state,
                "agent_response": response,
                "active_agent": None,
                "intent": None,
                "agent_state": {}  # 완료되었으므로 상태 초기화
            }

        logger.info(f"[예약] 리턴 직전 상태: active_agent={state.get('active_agent')}, intent={state.get('intent')}")
        
        # 4. 누락 슬롯이 있다면 → LLM이 만든 멘트로 계속 유도
        return {
            **state,
            "agent_response": message,
            "agent_state": {
                **state.get("agent_state", {}),
                "reservation": updated_slots
            },
            "active_agent": "reservation",
            "intent": "reservation"
        }

    except Exception as e:
        logger.warning(f"[예약] LLM 응답 파싱 실패: {e}")
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

    
    
    