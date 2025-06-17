from typing import Dict
import logging
from langchain_core.tools import tool



logger = logging.getLogger(__name__)
REQUIRED_SLOTS = ["departure", "arrival", "start_date", "end_date"]

@tool
def book_trip(slots: Dict[str, str]) -> str:
    """모든 예약 정보를 바탕으로 mock 예약을 수행합니다."""
    return (
        f"{slots['departure']}에서 {slots['arrival']}까지 "
        f"{slots['start_date']} ~ {slots['end_date']} 여행이 예약되었습니다!"
    )

def fill_slots(state: dict) -> dict:
    slots = state.get("slots", {})
    missing = [key for key in REQUIRED_SLOTS if key not in slots]
    logger.info(f"[예약] 현재 슬롯 상태: {slots}")
    logger.info(f"[예약] 누락 슬롯: {missing}")

    if not missing:
        response = book_trip(slots)
        return {
            **state,
            "agent_response": response,
            "used_agents": state["used_agents"] + ["reservation"],
        }

    # 누락된 슬롯이 있다면 LLM에게 질문 생성 요청
    next_question = f"{missing[0]} 정보를 알려주세요. 예시: '서울', '2025-07-01'"
    return {
        **state,
        "agent_response": next_question,
        "used_agents": state["used_agents"] + ["reservation"],
    }
