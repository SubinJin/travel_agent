#  - weather : 특정 지역과 날짜에 해당하는 날씨를 조회하려는 의도
INTENT_CLASSIFIER = """
다음 사용자 메시지를 기반으로 intent를 분류하세요.
가능한 intent와 intent에 대한 설명입니다. 
- calendar : 캘린더에 일정을 조회, 추가, 수정, 삭제하려는 의도
- menu : 음식 메뉴에 대한 대화 의도
- reservation : 여행 장소와 일정을 조회하고 예약하려는 의도
- unknown : 위 intent를 제외한 나머지 일상적인 대화 의도

사용자 메시지: "{user_message}"

intent만 한 단어로 출력하세요.
"""