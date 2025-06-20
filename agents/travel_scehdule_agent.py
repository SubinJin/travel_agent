import json
import re
from datetime import date
from typing import Dict
import logging
from langchain_core.tools import tool
from services.llm_judge import llm_judge
from llm.llm_client import LLMClient
from prompts.prompts import JUDGE_RESERVATION_SYSTEM, RESERVATION_SYSTEM_PROMPT, YES_NO_JUDGE_SYSTEM_PROMPT
from common.forms import ReservationSchema

logger = logging.getLogger(__name__)
REQUIRED_SLOTS = ["departure", "arrival", "start_date", "end_date"]
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

def llm_judges_cancel_intent(user_input: str) -> bool:
    system_prompt = JUDGE_RESERVATION_SYSTEM
    response = llm.chat_singleturn(user_input = user_input, system_prompt = system_prompt).strip().upper()
    logger.info(f"[스케줄] 스케줄 중단 판단 결과: {response}")
    return response == "YES"

@tool
def scehdule_finish(slots: Dict[str, str]) -> str:
    """모든 스케줄 정보를 바탕으로 여행 계획서를 작성해줍니다"""
    message = f"목적지는 {slots['arrival']}, {slots['start_date']} ~ {slots['end_date']} 여행 일정으로 계획이군요. 여행 계획서도 같이 작성할까요?"
    return message

def travel_scehdule_agent(state: dict) -> dict:
    """"여행 날짜와 장소 추천해주고 사용자의 여행 날짜와 장소를 입력받는 에이전트"""
    slots = state.get("agent_state", {}).get("travel_schedule", {})
    user_input = state.get("user_input", "")
    intent = state.get("intent")
    logger.info(f"[스케줄] 현재 사용자 발화: {user_input}")
    logger.info(f"[스케줄] 현재 슬롯 상태: {slots}")
    
    if intent == "schedule_confirm":
        # 사용자가 “아니오”라고 하면 탈출
        resp = llm_judge(user_input = user_input, system_prompt= YES_NO_JUDGE_SYSTEM_PROMPT)
        if resp == "NO" :
            return {
                **state,
                "agent_response": "알겠습니다. 다른 궁금하신점은 없으신가요?",
                "active_agent": None,
                "intent": None,
                "agent_state": {}
            }
        # “응” 계열이라면 바로 다음 에이전트로
        updated = state["agent_state"]["slots"]
        # response = scehdule_finish.invoke({"slots": updated})  # 필요하다면 메시지 재생성
        return {
            **state,
            "agent_response": "좋습니다. 관광, 먹거리, 멋진 풍경 등 원하는 여행 스타일을 대략적으로 말씀해주세요!",
            "active_agent": "travel_plan",
            "intent": "travel_plan",
            "agent_state": {"slots": updated},
            "travel_schedule_result": updated
        }

    system_prompt = RESERVATION_SYSTEM_PROMPT.format(
        departure = slots.get("departure", ""),
        arrival = slots.get("arrival", ""),
        start_date = slots.get("start_date", ""),
        end_date = slots.get("end_date", ""),
        user_input = user_input,
        today = date.today())
    logger.info(f"[스케줄] user_input : {user_input}")
    llm_output = llm.chat_multiturn_structured(system_prompt = system_prompt, user_input = user_input, response_format=ReservationSchema)
    
    logger.info(f"[스케줄] LLM 응답: {llm_output}")
    
    try:
        updated_slots = {
            "departure": llm_output.departure or slots.get("departure", ""),
            "arrival": llm_output.arrival or slots.get("arrival", ""),
            "start_date": llm_output.start_date or slots.get("start_date", ""),
            "end_date": llm_output.end_date or slots.get("end_date", ""),
        }
        message = llm_output.message

        # 3. 슬롯이 모두 채워졌다면 → 스케줄 완료
        missing = [k for k in REQUIRED_SLOTS if not updated_slots.get(k)]
        logger.info(f"[스케줄] 누락 슬롯: {missing}")

        if not missing:
            response = scehdule_finish.invoke({"slots": updated_slots})
            logger.info(f"[스케줄] 탈출할 때 : {updated_slots}")
            return {
                **state,
                "agent_response": response,
                "active_agent": "travel_schedule",
                "intent": "schedule_confirm",
                "agent_state": {"slots": updated_slots},
                "travel_schedule_result": updated_slots
            }

        logger.info(f"[스케줄] 리턴 직전 상태: active_agent={state.get('active_agent')}, intent={state.get('intent')}")
        
        # 4. 누락 슬롯이 있다면 → LLM이 만든 멘트로 계속 유도
        return {
            **state,
            "agent_response": message,
            "agent_state": {
                **state.get("agent_state", {}),
                "travel_schedule": updated_slots
            },
            "active_agent": "travel_schedule",
            "intent": "travel_schedule"
        }

    except Exception as e:
        logger.warning(f"[스케줄] LLM 응답 파싱 실패: {e}")
        return {
            **state,
            "agent_response": "죄송합니다. 방금 내용을 잘 이해하지 못했어요. 다시 말씀해 주세요.",
            "agent_state": {
                **state.get("agent_state", {}),
                "travel_plan_agent": slots
            },
            "active_agent": "travel_plan_agent",
            "intent": "travel_plan"
        }

    
    
    