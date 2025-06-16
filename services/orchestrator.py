# services/orchestrator.py

from typing import List
from typing import Literal
from llm.llm_client import LLMClient

# 사용할 수 있는 에이전트 이름들 정의 (현재는 2개만 예시)
ALL_AGENTS = {
    "calendar": "여행 일정을 만들었으니, 숙소도 정해볼까요?",
    "weather": "날씨도 확인하셨으니, 이제 일정을 계획해보시는 건 어때요?",
    "share": "계획을 다 짜셨다면 외부에 공유해보세요!",
    "budget": "예산 계산도 도와드릴 수 있어요!",
    "food": "맛집이나 관광지 추천도 필요하신가요?"
}

def suggest_next_action(used_agents: List[str]) -> str:
    # 안 쓴 agent 리스트
    remaining = [a for a in ALL_AGENTS.keys() if a not in used_agents]

    if not remaining:
        return ""  # 모두 사용했으면 추천 없음

    # 가장 먼저 안 쓴 거 하나 추천 (LLM 없이 rule 기반)
    next_agent = remaining[0]
    suggestion = ALL_AGENTS[next_agent]

    return f"{suggestion}"

IntentType = Literal["calendar", "weather", "share", "unknown"]

def llm_intent_router(state: dict) -> str:
    user_input = state["user_input"]
    client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

    intent = client.classify_intent(user_input)

    # 방어적으로 처리
    valid_intents = {"calendar", "weather", "menu", "share", "unknown"}
    return intent if intent in valid_intents else "unknown"

# router 노드용 (그대로 전달만)
def router_node(state: dict) -> dict:
    return state