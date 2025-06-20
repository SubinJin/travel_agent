import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_PLACE_KEY = os.getenv("GOOGLE_PLACE_KEY")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
CALENDAR_ID = os.getenv("CALENDAR_ID")