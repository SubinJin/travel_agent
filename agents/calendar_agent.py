import logging
from typing import Dict, Any
from llm.llm_client import LLMClient
from prompts.prompts import (
    JUDGE_CALENDAR_CRUD_SYSTEM_PROMPT,
    JUDGE_CALENDAR_CRUD_USER_PROMPT,
    CALENDAR_CREATE_SYSTEM_PROMPT,
    CALENDAR_READ_SYSTEM_PROMPT,
    CALENDAR_UPDATE_SYSTEM_PROMPT,
    CALENDAR_DELETE_SYSTEM_PROMPT,
)
from tools.calendar_api import (
    create_calendar_event,
    get_calendar_events,
    update_calendar_event,
    delete_calendar_event,
)

logger = logging.getLogger(__name__)
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

REQUIRED_SLOTS = {
    "create": ["summary", "location", "start_date", "end_date"],
    "update": ["event_id", "summary", "start_date", "end_date"],
    "delete": ["event_id"],
    "read": [],
}

def calendar_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    user_input = state["user_input"]
    agent_state = state.get("agent_state", {})
    action = agent_state.get("action")

    # 1. 어떤 CRUD 인텐트인지 판단
    if not action:
        action = llm.chat_singleturn(
            user_input=user_input,
            system_prompt=JUDGE_CALENDAR_CRUD_SYSTEM_PROMPT,
            user_prompt=JUDGE_CALENDAR_CRUD_USER_PROMPT
        ).strip().lower()
        agent_state["action"] = action
        logger.info(f"[캘린더] 사용자 의도 판단: {action}")

    # 2. 필요한 슬롯 채우기
    required_slots = REQUIRED_SLOTS[action]
    current_slots = agent_state.get("slots", {})
    missing = [slot for slot in required_slots if not current_slots.get(slot)]
    logger.info(f"[캘린더] 누락 슬롯: {missing}")

    if missing:
        # 프롬프트 선택
        if action == "create":
            system_prompt = CALENDAR_CREATE_SYSTEM_PROMPT
        elif action == "update":
            system_prompt = CALENDAR_UPDATE_SYSTEM_PROMPT
        elif action == "delete":
            system_prompt = CALENDAR_DELETE_SYSTEM_PROMPT
        else:
            system_prompt = CALENDAR_READ_SYSTEM_PROMPT

        slot_fill_response = llm.chat_singleturn(
            user_input=user_input,
            system_prompt=system_prompt
        )

        # JSON 파싱
        try:
            parsed_slots = eval(slot_fill_response)
            current_slots.update(parsed_slots)
            agent_state["slots"] = current_slots
        except Exception as e:
            logger.error(f"[캘린더] 슬롯 파싱 실패: {e}")
            return {
                **state,
                "agent_response": "입력을 이해하지 못했어요. 다시 말씀해주시겠어요?",
                "agent_state": agent_state,
            }

    # 3. 슬롯 다 채워졌으면 → API 호출 → 탈출
    missing = [slot for slot in required_slots if not agent_state["slots"].get(slot)]
    if not missing:
        try:
            response = ""
            slots = agent_state["slots"]
            if action == "create":
                response = create_calendar_event(slots)
            elif action == "read":
                response = get_calendar_events()
            elif action == "update":
                response = update_calendar_event(slots)
            elif action == "delete":
                response = delete_calendar_event(slots["event_id"])
        except Exception as e:
            logger.error(f"[캘린더] API 호출 실패: {e}")
            response = f"캘린더 작업 중 오류가 발생했어요: {e}"

        return {
            **state,
            "agent_response": response,
            "intent": None,
            "active_agent": None,
            "agent_state": {},  # 탈출
        }

    return {
        **state,
        "agent_response": f"계속해서 필요한 정보를 말씀해주세요. 현재 누락된 항목: {missing}",
        "agent_state": agent_state,
    }
