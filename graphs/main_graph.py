from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from agents.calendar_agent import create_itinerary
from agents.weather_agent import check_weather
from services.orchestrator import suggest_next_action, llm_intent_router, router_node
from llm.llm_client import LLMClient


# 상태 구조 정의
class GraphState(TypedDict):
    user_input: str
    agent_response: Optional[str]
    used_agents: List[str]


# 캘린더 에이전트 호출
def run_calendar(state: GraphState) -> GraphState:
    message = state["user_input"]
    response = create_itinerary.invoke({"destination": "부산", "date": "7월 1일"})
    follow_up = suggest_next_action(state["used_agents"] + ["calendar"])
    response += follow_up
    return {
        **state,
        "agent_response": response,
        "used_agents": state["used_agents"] + ["calendar"]
    }


# 날씨 에이전트 호출
def run_weather(state: GraphState) -> GraphState:
    message = state["user_input"]
    response = check_weather.invoke({"location": "부산"})
    follow_up = suggest_next_action(state["used_agents"] + ["weather"])
    response += follow_up
    return {
        **state,
        "agent_response": response,
        "used_agents": state["used_agents"] + ["weather"]
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
    return {
        **state,
        "agent_response": "죄송해요, 아직 그 기능은 준비 중이에요!",
    }


# 그래프 구성
def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("router", router_node)
    workflow.add_node("calendar", run_calendar)
    workflow.add_node("weather", run_weather)
    workflow.add_node("menu", run_menu)
    workflow.add_node("unknown", run_fallback)

    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        llm_intent_router,
        {
            "calendar": "calendar",
            "weather": "weather",
            "menu": "menu",
            "unknown": "unknown"
        }
    )
    workflow.add_edge("calendar", END)
    workflow.add_edge("weather", END)
    workflow.add_edge("menu", END)
    workflow.add_edge("unknown", END)

    return workflow.compile()