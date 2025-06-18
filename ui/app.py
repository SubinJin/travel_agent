import sys
import os
import logging
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

import streamlit as st
from graphs.main_graph import build_graph
from services.orchestrator import _client as llm_client

# Streamlit 페이지 세팅
st.set_page_config(page_title="여행 멀티 에이전트", layout="centered")
st.title("여행 일정 플래너")

# 세션 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {}
if "active_agent" not in st.session_state:
    st.session_state.active_agent = None
if "intent" not in st.session_state:
    st.session_state.intent = None

# 이전 대화 이력 출력
for sender, msg in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(msg)

# 채팅 입력창
user_input = st.chat_input("여행 계획에 대해 물어보세요!")

if user_input:
    # 사용자 발화 출력
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # FSM 호출
    graph = build_graph()
    state = {
        "user_input": user_input,
        "intent": st.session_state.intent,
        "agent_response": None,
        "active_agent": st.session_state.active_agent,
        "agent_state": st.session_state.agent_state,
        "chat_history": st.session_state.chat_history
    }
    result = graph.invoke(state)

    # 상태 반영
    st.session_state.agent_state = result.get("agent_state", {})
    st.session_state.active_agent = result.get("active_agent", None)
    st.session_state.intent = result.get("intent", None)
    final_response = result.get("agent_response", "죄송합니다. 응답을 생성하지 못했습니다.")

    # 스트리밍 출력
    partial = ""
    with st.chat_message("agent"):
        placeholder = st.empty()
        agent_message = result["agent_response"]
        partial = ""
        for c in agent_message:
            partial += c
            placeholder.markdown(partial)
            time.sleep(0.015)

    # 대화 이력 저장
    st.session_state.chat_history.append(("assistant", partial))