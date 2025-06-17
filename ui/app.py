# import sys
# import os
# import logging

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
# )
# logger = logging.getLogger(__name__)


# import streamlit as st
# from graphs.main_graph import build_graph
# from services.orchestrator import stream_agent

# # LangGraph 실행기 준비
# graph = build_graph()

# # Streamlit 페이지 세팅
# st.set_page_config(page_title="여행 멀티 에이전트", layout="centered")
# st.title("여행 일정 플래너")

# # 세션 초기화
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # 이전 대화 이력 출력
# for sender, msg in st.session_state.chat_history:
#     with st.chat_message(sender):
#         st.markdown(msg)

# # 채팅 입력창
# user_input = st.chat_input("여행 계획에 대해 물어보세요!")

# if user_input:
#     # 이전 기록에 유저 메시지 추가
#     st.session_state.chat_history.append(("user", user_input))
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     partial = ""
#     with st.chat_message("agent"):
#         placeholder = st.empty()
#         for chunk in stream_agent(user_input, st.session_state.chat_history):
#             delta = chunk.choices[0].delta.content or ""
#             partial += delta
#             placeholder.markdown(partial)
#     st.session_state.chat_history.append(("agent", partial))


import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

import streamlit as st
from services.orchestrator import llm_intent_router, stream_agent, _client as llm_client
from agents.reservation_agent import fill_slots

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

# if user_input:
#     # 1) 사용자 메시지 출력
#     st.session_state.chat_history.append(("user", user_input))
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     # 2) intent 예측 (reservation 흐름 유지)
#     if "active_flow" not in st.session_state:
#         st.session_state.active_flow = None

#     if st.session_state.active_flow == "reservation":
#         intent = "reservation"
#     else:
#         intent = llm_intent_router(user_input)
#         if intent == "reservation":
#             st.session_state.active_flow = "reservation"

#     # reservation 전용 상태 초기화/유지
#     if "reservation_slots" not in st.session_state:
#         st.session_state.reservation_slots = {}
#     if "reservation_history" not in st.session_state:
#         st.session_state.reservation_history = []

#     state = {
#         "user_input": user_input,
#         "intent": intent,
#         "agent_response": None,
#         "used_agents": [],
#         "slots": st.session_state.reservation_slots
#     }

#     # 3) 스트리밍 응답
#     partial = ""
#     with st.chat_message("agent"):
#         placeholder = st.empty()

#         if intent == "reservation":
#             # 1) 슬롯 상태 갱신 (이전 턴 대답 반영)
#             slot_state = fill_slots({
#                 **state,
#                 "agent_response": state.get("agent_response") or ""
#             })

#             # 2) LLM 호출 메시지 구성
#             messages = [
#                 {"role": "system", "content": f"현재 슬롯: {slot_state['slots']}"},
#                 {"role": "user",   "content": user_input},
#                 {"role": "system", "content": slot_state["agent_response"]},
#             ]

#             # 스트리밍
#             for chunk in llm_client.stream_chat(messages=messages):
#                 delta = chunk.choices[0].delta.content or ""
#                 partial += delta
#                 placeholder.markdown(partial)

#             # 마지막에 슬롯 최종 갱신
#             final_state = fill_slots({
#                 **slot_state,
#                 "agent_response": partial
#             })

#             # 세션에 slots, history 업데이트
#             st.session_state.reservation_slots = final_state["slots"]
#             st.session_state.reservation_history.append(partial)

#             # 모든 슬롯 완료 시 reservation 흐름 종료
#             if not final_state.get("missing_slots", []):
#                 st.session_state.active_flow = None

#         else:
#             # reservation 이외는 일반 채팅
#             for chunk in llm_client.stream_chat(
#                 messages=[{"role": "user", "content": user_input}]
#             ):
#                 delta = chunk.choices[0].delta.content or ""
#                 partial += delta
#                 placeholder.markdown(partial)
#             final_state = {**state, "agent_response": partial}

#     # 4) 최종 응답 저장 및 출력
#     st.session_state.chat_history.append(("agent", partial))
if user_input:
    # 1) 사용자 메시지 출력
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2) intent 예측 (reservation 흐름 유지)
    if "active_flow" not in st.session_state:
        st.session_state.active_flow = None

    if st.session_state.active_flow == "reservation":
        intent = "reservation"
    else:
        intent = llm_intent_router(user_input)
        if intent == "reservation":
            st.session_state.active_flow = "reservation"

    # reservation 전용 상태 초기화/유지
    if "reservation_slots" not in st.session_state:
        st.session_state.reservation_slots = {}
    if "reservation_history" not in st.session_state:
        st.session_state.reservation_history = []

    state = {
        "user_input": user_input,
        "intent": intent,
        "agent_response": None,
        "used_agents": [],
        "slots": st.session_state.reservation_slots
    }

    # 3) 스트리밍 응답
    partial = ""
    with st.chat_message("agent"):
        placeholder = st.empty()

        if intent == "reservation":
            # 1) 슬롯 상태 갱신 (이전 턴 대답 반영)
            slot_state = fill_slots({
                **state,
                "agent_response": state.get("agent_response") or ""
            })

            # 2) LLM 호출 메시지 구성 – user_input을 반드시 넣어야 슬롯이 채워집니다
            messages = [
                {"role": "system", "content": f"현재 슬롯: {slot_state['slots']}"},
                {"role": "user",   "content": user_input},
                {"role": "system", "content": slot_state["agent_response"]},
            ]

            # 스트리밍
            for chunk in llm_client.stream_chat(messages=messages):
                delta = chunk.choices[0].delta.content or ""
                partial += delta
                placeholder.markdown(partial)

            # 3) 마지막에 슬롯 최종 갱신
            final_state = fill_slots({
                **slot_state,
                "agent_response": partial
            })

            # 4) 세션에 slots, history 업데이트
            st.session_state.reservation_slots = final_state["slots"]
            st.session_state.reservation_history.append(partial)

            # 모든 슬롯 완료 시 reservation 흐름 종료
            if not final_state.get("missing_slots", []):
                st.session_state.active_flow = None

        else:
            # reservation 이외는 일반 채팅
            for chunk in llm_client.stream_chat(
                messages=[{"role": "user", "content": user_input}]
            ):
                delta = chunk.choices[0].delta.content or ""
                partial += delta
                placeholder.markdown(partial)
            final_state = {**state, "agent_response": partial}

    # 4) 최종 응답 저장 및 출력
    st.session_state.chat_history.append(("agent", partial))