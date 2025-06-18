from typing import TypedDict, Optional, Dict, Any, List

class GraphState(TypedDict):
    user_input: str
    intent: Optional[str]
    agent_response: Optional[str]
    active_agent: Optional[str]  # 현재 진행 중인 agent 이름
    agent_state: Dict[str, Any]  # 슬롯 등 agent 내부 상태
    chat_history: List[Dict[str, str]]