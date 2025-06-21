import json
import re
from typing import Dict, Any, List
import logging
from langchain_core.tools import tool
from llm.llm_client import LLMClient
from prompts.prompts import TRAVEL_PLANNING_SYSTEM_PROMPT
from common.forms import PlanSchema


logger = logging.getLogger(__name__)
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

def extract_json_string(text: str) -> str:
    """
    Extract the JSON substring by finding the first '{' and the last '}'.
    This handles cases where the model prepends natural language.
    """
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    # fallback: strip fences and return cleaned
    return re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()

@tool
def travel_plan_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """여행 계획서 작성 및 수정, 최종 확정 에이전트"""
    # 이전 대화 흐름을 state에서 가져오기 (메시지 키 혹은 chat_history 키)
    prev_messages: List[Dict[str, str]] = []
    if "messages" in state and state["messages"]:
        prev_messages = state.get("messages", [])
    elif "chat_history" in state and state["chat_history"]:
        prev_messages = state.get("chat_history", [])

    slots: Dict[str, str] = state.get("slots", {})
    user_input: str = state.get("user_input", "")

    logger.info(f"[여행플랜] user_input: {user_input}")
    logger.info(f"[여행플랜] previous slots: {slots}")
    logger.info(f"[여행플랜] previous messages (len={len(prev_messages)}): {prev_messages}")

    dep = slots.get("departure", "")
    arr = slots.get("arrival", "")
    start = slots.get("start_date", "")
    end = slots.get("end_date", "")

    # 시스템 프롬프트 생성
    system_content = TRAVEL_PLANNING_SYSTEM_PROMPT.format(
        dep=dep, arr=arr, start=start, end=end
    )

    # 전체 히스토리 구성: 시스템 → 이전 대화 → 유저
    history: List[Dict[str, str]] = []
    history.append({"role": "system", "content": system_content})
    history.extend(prev_messages)
    history.append({"role": "user", "content": user_input or "여행 일정 초안을 작성해 주세요."})

    logger.info(f"[여행플랜] Sending history (len={len(history)}) to LLM")

    # LLM 호출: chat_history 파라미터로 전체 컨텍스트 전달
    response = llm.chat_multiturn_structured(
        user_input="",
        system_prompt="",
        chat_history=history,
        response_format=PlanSchema

    )
    logger.info(f"[여행플랜] raw response: {str(response)}")
    # logger.info(response)
    
    
    itinerary = response.itinerary
    final_confirm = response.final_confirm.strip()
    message = response.message

    # JSON 파싱
    # try:
    #     data = json.loads(response)
    #     itinerary = data.get("itinerary", "")
    #     final_confirm = data.get("final_confirm", "").strip()
    #     message = data.get("message", "여행 계획 초안입니다.")
    # except Exception as e:
    #     logger.warning(f"[여행플랜] JSON 파싱 실패: {e}")
    #     itinerary = response
    #     final_confirm = ""
    #     message = response

    # 메시지 및 슬롯 업데이트
    assistant_msg = message + (f"\n\n{itinerary}" if itinerary else "")
    history.append({"role": "assistant", "content": assistant_msg})
    slots["itinerary"] = itinerary
    slots["final_confirm"] = final_confirm

    # 최종 확정 여부 확인
    logger.info(f"[여행플랜] final_confirm : {final_confirm}")
    if final_confirm == "YES" :
        logger.info(f"[여행플랜] 확정 진입 : {final_confirm}")
        logger.info(f"[여행플랜] 확정 일정 : {itinerary}")
        return {
            **state, 
            "agent_response": f"여행 계획이 확정되었습니다! 최종 일정:\n{itinerary}",
            "active_agent": None,
            "intent": None,
            "agent_state": {},
            "itinerary": itinerary,
            "messages": history
        }

    # 반복 수정 흐름 유지: messages 필드로 컨텍스트 전달
    return {
        "slots": slots,
        "messages": history,
        "agent_response": assistant_msg,
        "active_agent": "travel_plan",
        "intent": "travel_plan",
        "agent_state": {"slots": slots, "messages": history}
    }
