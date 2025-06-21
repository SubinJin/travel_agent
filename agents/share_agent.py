import logging
from typing import Dict, Any
from langchain_core.tools import tool

from llm.llm_client import LLMClient
from prompts.prompts import SHARE_FORMAT_SYSTEM_PROMPT
from tools.share_tool import generate_itinerary_pdf, generate_shareable_link
from common.forms import ShareSchema

logger = logging.getLogger(__name__)
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

# 공유 가능한 형식
VALID_FORMATS = ["pdf", "link"]

def share_itinerary_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """사용자의 여행 계획서를 pdf나 link 형식으로 제공하는 에이전트")"""
    logger.info("[공유] 에이전트 진입")
    user_input = state.get("user_input", "").strip()
    agent_state = state.setdefault("agent_state", {})
    slots = agent_state.setdefault("slots", {})
    history = agent_state.setdefault("chat_history", [])

    # 1. 사용자의 마지막 발화 저장
    history.append({"role": "user", "content": user_input})

    # 2. 일정 확인
    itinerary = state.get("itinerary")
    if not itinerary:
        response = "먼저 여행 일정을 생성한 후 공유해 주세요."
        return {
            **state,
            "agent_response": response,
            "intent": None,
            "active_agent": None,
            "agent_state": {}
        }

    # 3. 구조화된 멀티턴 대화로 포맷 정보 얻기
    if "share_format" not in slots:
        result = llm.chat_multiturn_structured(user_input=user_input, system_prompt=SHARE_FORMAT_SYSTEM_PROMPT, chat_history=history, response_format=ShareSchema)
        logger.info(f"[공유] llm return: {result}")
        msg = result.message
        fmt = result.share_format
        # 대화 메시지 추가
        history.append({"role": "assistant", "content": msg})

        # share_format 검증
        if fmt in VALID_FORMATS:
            slots["format_type"] = fmt
            agent_state["slots"] = slots
        else:
            history.append({"role": "assistant", "content": msg})
            return {
                **state,
                "agent_response": msg,
                "agent_state": agent_state
            }

    # 4. 슬롯 준비 완료 → API 호출
    fmt = slots.get("format_type")
    try:
        if fmt == "pdf":
            result = generate_itinerary_pdf(itinerary)
        else:
            result = generate_shareable_link(itinerary)
        response = result
    except Exception as e:
        logger.error(f"[공유] API 호출 실패: {e}")
        response = f"일정 공유 중 오류가 발생했습니다: {e}"

    # 최종 응답 추가
    history.append({"role": "assistant", "content": response})

    # 5. 공유 후 상태 초기화
    return {
        **state,
        "agent_response": response,
        "intent": None,
        "active_agent": None,
        "agent_state": {}
    }
