
import logging
from llm.llm_client import LLMClient
from graphs.graph_state import GraphState

logger = logging.getLogger(__name__)

llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

def llm_intent_router(state: GraphState) -> GraphState:
    user_input = state["user_input"]

    if state.get("active_agent"):
        return state
    # 인텐트 분류
    intent = llm.classify_intent(user_input)
    logger.info(f"[라우터] 인텐트 추론 결과: {intent} | 입력: {user_input}")

    valid = {"calendar", "location_search", "travel_schedule", "share_itinerary", "unknown"}
    intent = intent if intent in valid else "unknown"
    if not intent:
        intent = "unknown"

    return {
        **state,
        "intent": intent,
        "active_agent": intent if intent != "unknown" else None
    }

