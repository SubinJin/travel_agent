from langchain.tools import tool

@tool
def create_itinerary(destination: str, date: str) -> str:
    """사용자가 지정한 여행지와 날짜를 기반으로 일정을 생성합니다."""
    return f"{date}에 {destination}로 떠나는 여행 일정을 구성했어요! 오전에는 관광, 오후에는 맛집 탐방 어떠세요?"