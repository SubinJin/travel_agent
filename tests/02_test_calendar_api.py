import pytest
import time
import logging
from tools.calendar_api import (
    create_calendar_event,
    get_calendar_events,
    update_calendar_event,
    delete_calendar_event
)


logger = logging.getLogger(__name__)

# 공유: fixture로 생성한 일정 ID 저장
event_id_holder = {}
def sanitize_event_id(event_id: str) -> str:
    # 좌우 어떤 괄호라도 제거
    return event_id.strip("()")


@pytest.mark.order(1)
def test_create_event():
    slots = {
        "summary": "pytest 테스트 일정",
        "location": "서울",
        "start_date": "2025-07-21",
        "end_date": "2025-07-23"
    }
    result = create_calendar_event(slots)
    assert "일정이 등록되었어요" in result

    # event_id를 get_calendar_events로 찾아서 저장
    events = get_calendar_events()
    for line in events.splitlines():
        if "pytest 테스트 일정" in line and "ID:" in line:
            event_id = line.split("ID:")[1].strip()
            event_id_holder["event_id"] = event_id
            break

    assert "event_id" in event_id_holder

@pytest.mark.order(2)
def test_get_events():
    result = get_calendar_events()
    assert "일정" in result

@pytest.mark.order(3)
def test_update_event():
    event_id = event_id_holder.get("event_id")
    event_id = sanitize_event_id(event_id)
    assert event_id is not None

    slots = {
        "event_id": event_id,
        "summary": "수정된 pytest 일정",
        "start_date": "2025-07-24",
        "end_date": "2025-07-25"
    }
    result = update_calendar_event(slots)
    assert "일정이 수정되었어요" in result

@pytest.mark.order(4)
def test_delete_event():
    event_id = event_id_holder.get("event_id")
    event_id = sanitize_event_id(event_id)
    assert event_id is not None

    result = delete_calendar_event(event_id)
    assert "일정이 삭제되었어요" in result
