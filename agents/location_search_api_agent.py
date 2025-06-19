import logging
from typing import Dict, Any, List
from llm.llm_client import LLMClient
from prompts.prompts import SEARCH_RESULT_VALID_SYSTEM_PROMPT, SEARCH_RESULT_VALID_USER_PROMPT, SEARCH_QUERY_CLEANSE_SYSTEM_PROMPT, SEARCH_QUERY_CLEANSE_USER_PROMPT
from tools.location_search_api import search_places

logger = logging.getLogger(__name__)
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

# def llm_judges_cancel_api(user_input: str) -> bool:
#     """사용자가 API 검색을 중단하고자 하는지 LLM으로 판단"""
#     response = llm.chat_singleturn(
#         user_input=user_input,
#         system_prompt=JUDGE_LOCATION_SEARCH_API_CANCEL
#     ).strip().upper()
#     logger.info(f"[API 에이전트] 검색 중단 판단 결과: {response}")
#     return response == "YES"

def location_search_api_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    slots = state.get("agent_state", {}).get("location_search", {})

    # 0) 검색 중단 의사 판단
    # if llm_judges_cancel_api(user_input):
    #     return {
    #         **state,
    #         "agent_response": "API 검색을 중단합니다.",
    #         "active_agent": None,
    #         "intent": None,
    #         "agent_state": {}
    #     }
    
    user_input = state.get("user_input", "").strip()
    region = slots.get("selected_place")
    
    # 0) 사용자가 '그만'이라고 입력하면 API 검색 종료
    if user_input.lower().startswith("그만"):
        return {
            **state,
            "agent_response": "상세 검색을 종료합니다. 다른 궁금한점을 물어보세요!",
            "active_agent": None,
            "intent": None,
            "agent_state": {}
        }
    
    logger.info(f"[API 에이전트] 사용자 입력: {user_input}")
    logger.info(f"[API 에이전트] 지역: {region}")

    # 검색 쿼리 정제
    system_prompt = SEARCH_QUERY_CLEANSE_SYSTEM_PROMPT
    user_prompt = SEARCH_QUERY_CLEANSE_USER_PROMPT.format(region = region, query = user_input)
    response = llm.chat_singleturn(user_input = user_prompt, system_prompt = system_prompt)
    logger.info(f"[API 에이전트] API 검색 키워드 : {response}")
    
    # API 호출
    results: List[Dict[str, Any]] = search_places(search_query=response)
    # 응답 메시지 생성
    lines = [f"{i+1}. {p['name']} (평점: {p.get('rating','?')}) - {p.get('formatted_address','주소 없음')}" 
             for i, p in enumerate(results)]
    
    system_prompt = SEARCH_RESULT_VALID_SYSTEM_PROMPT
    user_prompt = SEARCH_RESULT_VALID_USER_PROMPT.format(region = region, query = user_input, lines = lines)
    response = llm.chat_singleturn(user_input = user_prompt, system_prompt = system_prompt)
    
    message = "상세 검색 결과입니다:\n" + response

    # 2) 재검색 안내
    followup = ("\n\n 추가로 다른 키워드로 검색하시려면 키워드를 입력하세요. '그만'을 입력하시면 종료됩니다.")
    message += followup

    # 3) 상태 업데이트
    slots.update({"api_active": True, "query": region + ' ' + user_input})
    state["agent_state"]["location_search"] = slots

    # 4) 에이전트 유지
    return {
        **state,
        "agent_response": message,
        "active_agent": "location_search_api",
        "intent": "location_search_api",
        "agent_state": state.get("agent_state", {})
    }
