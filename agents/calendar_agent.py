import logging
import re
from datetime import date
from pydantic import BaseModel
from typing import Dict, Any
from llm.llm_client import LLMClient
from prompts.prompts import JUDGE_CALENDAR_CRUD_SYSTEM_PROMPT, JUDGE_CALENDAR_CRUD_USER_PROMPT, CALENDAR_CREATE_SYSTEM_PROMPT, CALENDAR_READ_SYSTEM_PROMPT, CALENDAR_UPDATE_SYSTEM_PROMPT, CALENDAR_DELETE_SYSTEM_PROMPT
from common.forms import CalendarCreateSchema, CalendarReadSchema, CalendarUpdateSchema, CalendarDeleteSchema
from tools.calendar_api import create_calendar_event, get_calendar_events, update_calendar_event, delete_calendar_event

logger = logging.getLogger(__name__)
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

REQUIRED_SLOTS = {
    "create": ["summary", "location", "start_date", "end_date"],
    "update": ["event_id", "summary", "start_date", "end_date"],
    "delete": ["event_id"],
    "read": [],
}

def extract_id_from_message(msg: str) -> str:
    m = re.search(r"\(([^\)]+)\)", msg)
    return m.group(1) if m else None

def calendar_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    user_input = state["user_input"]
    agent_state = state.setdefault("agent_state", {})

    # 1) history 초기화
    history = agent_state.setdefault("chat_history", [])
    # 매턴마다 유저 메시지 쌓기
    history.append({"role": "user", "content": user_input})

    # 2) intent 판단 (한 번만 실행)
    action = agent_state.get("action")
    if not action:
        resp = llm.chat_multiturn(
            user_input=user_input,
            system_prompt=JUDGE_CALENDAR_CRUD_SYSTEM_PROMPT,
            chat_history=history
        ).strip().lower()
        agent_state["action"] = action = resp
        history.append({"role": "assistant", "content": resp})
        logger.info(f"[캘린더] 의도: {action}")

    # 3) 슬롯 채우기
    required = REQUIRED_SLOTS[action]
    slots = agent_state.setdefault("slots", {})
    missing = [s for s in required if not slots.get(s)]
    logger.info(f"[캘린더] 누락 슬롯: {missing}")

    if missing:
        # 적절한 프롬프트 고르기
        prompts = {
            "create": CALENDAR_CREATE_SYSTEM_PROMPT,
            "read":   CALENDAR_READ_SYSTEM_PROMPT,
            "update": CALENDAR_UPDATE_SYSTEM_PROMPT.format(today = date.today()),
            "delete": CALENDAR_DELETE_SYSTEM_PROMPT,
        }
        # 적절한 포맷 고르기
        response_format = {
            "create": CalendarCreateSchema,
            "read":   CalendarReadSchema,
            "update": CalendarUpdateSchema,
            "delete": CalendarDeleteSchema,
        }
        # LLM 호출
        slot_model: BaseModel = llm.chat_multiturn_structured(
            user_input=user_input,
            system_prompt=prompts[action],
            chat_history=history,
            response_format=response_format[action]
        )
        # history에 쌓기
        history.append({"role": "assistant", "content": slot_model.message})

        # JSON 파싱
        logger.info(f"[캘린더] LLM 답변 : {slot_model}")
        slot_data = slot_model.dict(exclude_unset=True)
        slots.update(slot_data)
        agent_state["slots"] = slots

    # 4) 모든 슬롯 채워졌으면 API 호출
    missing = [s for s in required if not slots.get(s)]
    if not missing:
        # (생성 시 ID 추출 로직 포함)
        if action == "create":
            msg = create_calendar_event(slots)
            evt_id = extract_id_from_message(msg)
            if evt_id:
                slots["event_id"] = evt_id
            response = msg
        elif action == "read":
            response = get_calendar_events()
        elif action == "update":
            response = update_calendar_event(slots)
        else:  # delete
            response = delete_calendar_event(slots["event_id"])

        history.append({"role": "assistant", "content": response})
        return {
            **state,
            "agent_response": response,
            "intent": None,
            "active_agent": None,
            "agent_state": {},  # 초기화
        }

    # 아직 슬롯 남았으면 계속 질문
    prompt = slot_model.message
    history.append({"role": "assistant", "content": prompt})
    return {
        **state,
        "agent_response": prompt,
        "agent_state": agent_state,
    }
