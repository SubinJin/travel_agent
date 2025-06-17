import logging
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Dict, Any
from services.orchestrator import llm_intent_router #,router_node
from llm.llm_client import LLMClient
from agents.reservation_agent import fill_slots

logger = logging.getLogger(__name__)

# 상태 구조 정의
class GraphState(TypedDict):
    user_input: str
    intent: Optional[str]
    agent_response: Optional[str]
    used_agents: List[str]
    slots: Dict[str, Any]  # 예약정보, 장소, 날짜 등
    plan: Optional[str]  # 전체 계획서
    calendar_schedule: List[Dict]  # 캘린더 형태로 가공된 일정
    share_link: Optional[str]
    

def router_node(state: GraphState) -> GraphState:
    intent = llm_intent_router(state["user_input"])
    logger.info(f"[라우터] 인텐트 라우팅 결과: {intent}")
    return {**state, "intent": intent}

# 예약 에이전트 호출    
def run_reservation(state: GraphState) -> GraphState:
    logger.info("[run_reservation] 예약 노드 진입")
    return fill_slots(state)


# 캘린더 에이전트 호출
def run_calendar(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

    response = client.chat(user_input)

    return {
        **state,
        "agent_response": response,
        "used_agents": state["used_agents"] + ["menu"]
    }


# 날씨 에이전트 호출
def run_weather(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

    response = client.chat(user_input)

    return {
        **state,
        "agent_response": response,
        "used_agents": state["used_agents"] + ["menu"]
    }


# 메뉴 (그냥 GPT 호출해서 응답 리턴)
def run_menu(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

    response = client.chat(user_input)

    return {
        **state,
        "agent_response": response,
        "used_agents": state["used_agents"] + ["menu"]
    }


# fallback
def run_fallback(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()

    response = client.chat(user_input)

    return {
        **state,
        "agent_response": response,
        "used_agents": state["used_agents"] + ["menu"]
    }


# 그래프 구성
def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("router", router_node)
    workflow.add_node("calendar", run_calendar)
    # workflow.add_node("weather", run_weather)
    workflow.add_node("menu", run_menu)
    workflow.add_node("reservation", run_reservation)
    workflow.add_node("unknown", run_fallback)

    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        # llm_intent_router,
        lambda state: state["intent"],
        {
            "calendar": "calendar",
            # "weather": "weather",
            "menu": "menu",
            "reservation" : "reservation",
            "unknown": "unknown"
        }
    )
    workflow.add_edge("calendar", END)
    # workflow.add_edge("weather", END)
    workflow.add_edge("menu", END)
    workflow.add_edge("reservation", END)
    workflow.add_edge("unknown", END)

    return workflow.compile()