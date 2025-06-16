import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from graphs.main_graph import build_graph

# LangGraph 실행기 준비
graph = build_graph()

# Streamlit 페이지 세팅
st.set_page_config(page_title="여행 멀티 에이전트", layout="centered")
st.title("여행 일정 플래너")

# 세션 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 이전 대화 이력 출력
for sender, msg in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(msg)

# 채팅 입력창
user_input = st.chat_input("여행 계획에 대해 물어보세요!")

if user_input:
    # 이전 기록에 유저 메시지 추가
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # LangGraph 실행
    inputs = {
        "user_input": user_input,
        "agent_response": None,
        "used_agents": [],
    }

    result = graph.invoke(inputs)
    response = result["agent_response"]

    # 응답 출력
    with st.chat_message("agent"):
        st.markdown(response)
    st.session_state.chat_history.append(("agent", response))