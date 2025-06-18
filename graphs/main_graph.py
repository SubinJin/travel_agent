import logging
from langgraph.graph import StateGraph, END
from services.orchestrator import llm_intent_router #,router_node
from llm.llm_client import LLMClient
from graphs.graph_state import GraphState
from agents.reservation_agent import fill_slots

from prompts.prompts import AGENT_DEFAULT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()
    
def router_node(state: GraphState) -> GraphState:
    next_state = llm_intent_router(state)
    intent = next_state["intent"]
    logger.info(f"[라우터] 인텐트 라우팅 결과: {intent}")
    return next_state

# 예약 에이전트 호출    
def run_reservation(state: GraphState) -> GraphState:
    logger.info("[run_reservation] 예약 노드 진입")
    result = fill_slots(state)

    # LangGraph에 선언된 GraphState 필드만 추출해서 전달
    return {
        "user_input": result["user_input"],
        "intent": result["intent"],
        "agent_response": result["agent_response"],
        "active_agent": result["active_agent"],
        "agent_state": result["agent_state"],
        "chat_history": result.get("chat_history", []),
    }


# 캘린더 에이전트 호출
def run_calendar(state: GraphState) -> GraphState:
    user_input = state["user_input"]

    response = client.chat(user_input)

    return {
        **state,
        "agent_response": response
    }


# 날씨 에이전트 호출
def run_weather(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    response = client.chat(user_input)

    return {
        **state,
        "agent_response": response
    }


# 메뉴 (그냥 GPT 호출해서 응답 리턴)
def run_menu(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    response = client.chat(user_input)

    return {
        **state,
        "agent_response": response
    }


# fallback
def run_fallback(state: GraphState) -> GraphState:
    system_prompt = AGENT_DEFAULT_SYSTEM_PROMPT
    user_input = state["user_input"]
    logger.info(f"[일반] user_input : {user_input}")
    chat_history = state.get("chat_history", [])
    formatted_history = [{"role": r, "content": c} for (r, c) in chat_history]
    logger.info(f"[일반] chat_history : {formatted_history}")
    
    response = client.chat(user_input = user_input, system_prompt = system_prompt, chat_history = formatted_history)

    return {
        **state,
        "agent_response": response
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