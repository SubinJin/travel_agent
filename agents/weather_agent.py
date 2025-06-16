from langchain.tools import tool

@tool
def check_weather(location: str) -> str:
    """입력된 여행지의 날씨를 알려줍니다. (임시 텍스트)"""
    return f"{location}의 날씨는 맑고 화창할 것으로 예상돼요! 낮 최고 25도입니다."