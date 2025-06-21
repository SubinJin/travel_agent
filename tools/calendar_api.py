import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
from config.config import get_config

config = get_config()
# Google Calendar 설정
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = config.get("SERVICE_ACCOUNT_FILE")
CALENDAR_ID = config.get("CALENDAR_ID")

# 인증 및 서비스 객체 생성
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)

def create_calendar_event(slots: dict) -> str:
    """일정 생성"""
    event = {
        'summary': slots.get('summary', '여행 일정'),
        'location': slots.get('location', ''),
        'description': '자동 등록된 여행 일정입니다.',
        'start': {
            'date': slots['start_date'],
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'date': slots['end_date'],
            'timeZone': 'Asia/Seoul',
        },
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return f"일정이 등록되었어요: {created_event.get('htmlLink')}"

def get_calendar_events() -> str:
    """가장 가까운 5개의 일정 조회"""
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now,
        maxResults=5,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        return "조회 가능한 일정이 없어요."

    response = "가까운 일정들을 알려드릴게요:\n"
    for event in events:
        start = event['start'].get('date', event['start'].get('dateTime'))
        response += f"- {start}: {event.get('summary')} (ID: {event.get('id')})\n"
    return response

def update_calendar_event(slots: dict) -> str:
    """기존 일정 수정"""
    event_id = slots['event_id']
    event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

    event['summary'] = slots.get('summary', event['summary'])
    event['start'] = {
        'date': slots['start_date'],
        'timeZone': 'Asia/Seoul',
    }
    event['end'] = {
        'date': slots['end_date'],
        'timeZone': 'Asia/Seoul',
    }

    updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
    return f"일정이 수정되었어요: {updated_event.get('htmlLink')}"

def delete_calendar_event(event_id: str) -> str:
    """일정 삭제"""
    service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    return "일정이 삭제되었어요."
