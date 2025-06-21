import logging
from langgraph.graph import StateGraph, END

from llm.llm_client import LLMClient
from graphs.graph_state import GraphState
from services.orchestrator import llm_intent_router

from agents.travel_scehdule_agent import travel_scehdule_agent
from agents.travel_plan_agent import travel_plan_agent
from agents.location_search_agent import location_search_agent
from agents.location_search_api_agent import location_search_api_agent
from agents.calendar_agent import calendar_agent
from agents.share_agent import share_itinerary_agent

from prompts.prompts import AGENT_DEFAULT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
llm = LLMClient(service_name="openai", model_name="gpt-4o").get_client()
    
def router_node(state: GraphState) -> GraphState:
    next_state = llm_intent_router(state)
    intent = next_state["intent"]
    logger.info(f"[라우터] 인텐트 라우팅 결과: {intent}")
    return next_state


# 장소 검색 에이전트 호출    
def run_travel_plan(state: GraphState) -> GraphState:
    logger.info("[run_travel_plan] 여행 계획서 노드 진입")
    prev_agent_state = state.get("agent_state", {})
    tool_state = {
        "slots": prev_agent_state.get("slots", {}),
        "messages": prev_agent_state.get("messages", []),
        "user_input": state.get("user_input", "")
    }
    
    result = travel_plan_agent.invoke({"state": tool_state})

    return {
        "user_input": state.get("user_input", ""),
        "intent": result.get("intent", state.get("intent")),
        "agent_response": result["agent_response"],
        "active_agent": result.get("active_agent"),
        "agent_state": {
            "slots": result.get("slots", tool_state["slots"]),
            "messages": result.get("messages", tool_state["messages"])
        },
        "itinerary": result.get("itinerary"),
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
        "itinerary": state.get("itinerary"),
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
        "itinerary": state.get("itinerary"),
        "chat_history": result.get("chat_history", []),
    }

# 예약 에이전트 호출    
def run_travel_scehdule_agent(state: GraphState) -> GraphState:
    logger.info("[run_travel_scehdule_agent] 여행계획서 작성 노드 진입")
    result = travel_scehdule_agent(state)

    # LangGraph에 선언된 GraphState 필드만 추출해서 전달
    return {
        "user_input": result["user_input"],
        "intent": result["intent"],
        "agent_response": result["agent_response"],
        "active_agent": result["active_agent"],
        "agent_state": result["agent_state"],
        "itinerary": state.get("itinerary"),
        "chat_history": result.get("chat_history", []),
    }

# 캘린더 에이전트 호출
def run_calendar(state: GraphState) -> GraphState:
    logger.info("[run_calendar] 캘린더 CRUD 노드 진입")
    result = calendar_agent(state)

    return {
        "user_input":    result["user_input"],
        "intent":        result.get("intent"),
        "agent_response":result.get("agent_response"),
        "active_agent":  result.get("active_agent"),
        "agent_state":   result.get("agent_state", {}),
        "itinerary":      state.get("itinerary"),
        "chat_history":  result.get("agent_state", {}).get("chat_history", []),
    }
   
# 여행계획 공유 에이전트 호출 
def run_share_itinerary(state: GraphState) -> GraphState:
    logger.info("[run_share] 공유 에이전트 노드 진입")
    if not state.get("itinerary"):
        state["itinerary"] = state.get("agent_state", {}).get("slots", {}).get("itinerary")
    result = share_itinerary_agent(state)

    return {
        "user_input":     result.get("user_input"),
        "intent":         result.get("intent"),
        "agent_response": result.get("agent_response"),
        "active_agent":   result.get("active_agent"),
        "agent_state":    result.get("agent_state", {}),
        "itinerary":      state.get("itinerary"),
        "chat_history":   result.get("agent_state", {}).get("chat_history", []),
    }

# normal
def run_normal(state: GraphState) -> GraphState:
    system_prompt = AGENT_DEFAULT_SYSTEM_PROMPT
    user_input = state["user_input"]
    logger.info(f"[일반] user_input : {user_input}")
    chat_history = state.get("chat_history", [])
    formatted_history = [{"role": r, "content": c} for (r, c) in chat_history]
    logger.info(f"[일반] chat_history : {formatted_history}")
    
    response = llm.chat_multiturn(user_input = user_input, system_prompt = system_prompt, chat_history = formatted_history)

    return {
        **state,
        "itinerary": state.get("itinerary"),
        "agent_response": response
    }


# 그래프 구성
def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("router", router_node)
    workflow.add_node("calendar", run_calendar)
    workflow.add_node("location_search", run_location_search)
    workflow.add_node("location_search_api", run_location_search_api)
    workflow.add_node("travel_plan", run_travel_plan)
    workflow.add_node("travel_schedule", run_travel_scehdule_agent)
    workflow.add_node("share_itinerary", run_share_itinerary)
    workflow.add_node("unknown", run_normal)

    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {
            "calendar": "calendar",
            "location_search" : "location_search",
            "location_search_api" : "location_search_api", 
            "travel_plan" : "travel_plan",
            "travel_schedule": "travel_schedule",
            "share_itinerary" : "share_itinerary", 
            "unknown": "unknown"
        }
    )
    workflow.add_edge("calendar", END)
    workflow.add_edge("location_search", END)
    workflow.add_edge("location_search_api", END)
    workflow.add_edge("travel_plan", END)
    workflow.add_edge("travel_schedule", END)
    workflow.add_edge("share_itinerary", END)
    workflow.add_edge("unknown", END)

    return workflow.compile()