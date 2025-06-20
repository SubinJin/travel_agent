import logging
from langgraph.graph import StateGraph, END
from services.orchestrator import llm_intent_router #,router_node
from llm.llm_client import LLMClient
from graphs.graph_state import GraphState
from agents.reservation_agent import fill_slots
from agents.location_search_agent import location_search_agent
from agents.location_search_api_agent import location_search_api_agent
from agents.travel_plan_agent import travel_plan_agent

from prompts.prompts import AGENT_DEFAULT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()
    
def router_node(state: GraphState) -> GraphState:
    next_state = llm_intent_router(state)
    intent = next_state["intent"]
    logger.info(f"[라우터] 인텐트 라우팅 결과: {intent}")
    return next_state


# 장소 검색 에이전트 호출    
def run_travel_plan(state: GraphState) -> GraphState:
    # logger.info("[run_travel_plan] 여행 계획서 노드 진입")
    # result = travel_plan_agent(state)
    
    # # LangGraph에 선언된 GraphState 필드만 추출해서 전달
    # return {
    #     "user_input": result["user_input"],
    #     "intent": result["intent"],
    #     "agent_response": result["agent_response"],
    #     "active_agent": result["active_agent"],
    #     "agent_state": result["agent_state"],
    #     "chat_history": result.get("chat_history", []),
    # }
    logger.info("[run_travel_plan] 여행 계획서 노드 진입")
    # 1) GraphState.agent_state 안에 들어있는 slots, messages 꺼내기
    prev_agent_state = state.get("agent_state", {})
    tool_state = {
        "slots": prev_agent_state.get("slots", {}),
        "messages": prev_agent_state.get("messages", []),
        "user_input": state.get("user_input", "")
    }

    # 2) travel_plan_agent 호출 (tool_state 구조에 맞춰서)
    result = travel_plan_agent.invoke({"state": tool_state})

    # 3) 리턴된 result 들을 다시 GraphState 필드로 매핑
    return {
        "user_input": state.get("user_input", ""),
        "intent": result.get("intent", state.get("intent")),
        "agent_response": result["agent_response"],
        "active_agent": result.get("active_agent"),
        "agent_state": {
            "slots": result.get("slots", tool_state["slots"]),
            "messages": result.get("messages", tool_state["messages"])
        },
        # LangGraph 쪽에서 'chat_history' 로 쓰고 싶으면 messages 를 그대로 넣어주세요
        "chat_history": result.get("messages", tool_state["messages"])
    }

# 장소 검색 에이전트 호출    
def run_location_search(state: GraphState) -> GraphState:
    logger.info("[run_location_search] 검색 노드 진입")
    result = location_search_agent(state)
    
    # LangGraph에 선언된 GraphState 필드만 추출해서 전달
    return {
        "user_input": result["user_input"],
        "intent": result["intent"],
        "agent_response": result["agent_response"],
        "active_agent": result["active_agent"],
        "agent_state": result["agent_state"],
        "chat_history": result.get("chat_history", []),
    }
    
# 장소 상세 검색 API 에이전트 호출
def run_location_search_api(state: GraphState) -> GraphState:
    logger.info("[run_location_search_api] API 검색 노드 진입")
    result = location_search_api_agent(state)
    
    # LangGraph에 선언된 GraphState 필드만 추출해서 전달
    return {
        "user_input": result["user_input"],
        "intent": result["intent"],
        "agent_response": result["agent_response"],
        "active_agent": result["active_agent"],
        "agent_state": result["agent_state"],
        "chat_history": result.get("chat_history", []),
    }


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

    response = client.chat_multiturn(user_input)

    return {
        **state,
        "agent_response": response
    }


# 날씨 에이전트 호출
def run_weather(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    response = client.chat_multiturn(user_input)

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
    
    response = client.chat_multiturn(user_input = user_input, system_prompt = system_prompt, chat_history = formatted_history)

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
    workflow.add_node("reservation", run_reservation)
    workflow.add_node("location_search", run_location_search)
    workflow.add_node("location_search_api", run_location_search_api)
    workflow.add_node("travel_plan", run_travel_plan)
    workflow.add_node("unknown", run_fallback)

    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        # llm_intent_router,
        lambda state: state["intent"],
        {
            "calendar": "calendar",
            # "weather": "weather",
            # "menu": "menu",
            "reservation" : "reservation",
            "location_search" : "location_search",
            "location_search_api" : "location_search_api", 
            "travel_plan" : "travel_plan",
            "unknown": "unknown"
        }
    )
    workflow.add_edge("calendar", END)
    # workflow.add_edge("menu", END)
    workflow.add_edge("reservation", END)
    workflow.add_edge("location_search", END)
    workflow.add_edge("location_search_api", END)
    workflow.add_edge("travel_plan", END)
    workflow.add_edge("unknown", END)

    return workflow.compile()