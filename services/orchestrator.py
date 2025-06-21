
import logging
from llm.llm_client import LLMClient
from graphs.graph_state import GraphState

logger = logging.getLogger(__name__)

_client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

def llm_intent_router(state: GraphState) -> GraphState:
    user_input = state["user_input"]

    # 이미 진행 중인 agent가 있다면 intent 판단 생략
    if state.get("active_agent"):
        return state

    # 인텐트 분류
    intent = _client.classify_intent(user_input)
    logger.info(f"[라우터] 인텐트 추론 결과: {intent} | 입력: {user_input}")

    valid = {"calendar", "reservation", "location_search", "travel_plan", "share_itinerary", "unknown"}
    intent = intent if intent in valid else "unknown"
    if not intent:
        intent = "unknown"

    return {
        **state,
        "intent": intent,
        "active_agent": intent if intent != "unknown" else None
    }

def stream_agent(user_input: str, chat_history: list[tuple[str, str]]):
    # 1) 과거 대화 맥락을 messages 리스트로 변환
    messages = []
    for sender, text in chat_history:
        role = "user" if sender == "user" else "assistant"
        messages.append({"role": role, "content": text})
    # 2) 새 user 입력 추가
    intent = llm_intent_router(user_input)
    prompt = f"[{intent.upper()} Agent] 사용자 요청: {user_input}"
    messages.append({"role": "user", "content": prompt})

    # 3) 스트리밍
    for chunk in _client.stream_chat(messages):
        yield chunk

def simple_intent_router(user_input: str) -> str:
    intent = _client.classify_intent(user_input)
    logger.info(f"[App] 인텐트 추론 결과: {intent} | 입력: {user_input}")
    valid = {"calendar", "weather", "menu", "reservation", "unknown"}
    return intent if intent in valid else "unknown"


# # router 노드용 (그대로 전달만)
# def router_node(state: dict) -> dict:
#     return state

