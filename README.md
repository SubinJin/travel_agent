# 여행 일정 계획 멀티 에이전트 시스템

## 📚 프로젝트 개요
여행 일정 계획을 지원하는 멀티 에이전트 기반의 AI 시스템입니다. 자연스러운 대화를 통해 사용자가 여행 장소를 검색하고, 일정 계획 및 관리를 할 수 있도록 설계되었습니다.

## 📌 기본 기능

- 대화 기반 여행 장소 추천, 검색 및 Google Place API를 활용한 상세 검색
- 대화 기반 여행 일정 수립, 세부 여행 계획서 작성
- 캘린더 등록, 조회, 수정, 삭제 기능 제공 (Google Calendar API)
- 여행 계획서를 외부에 공유 (PDF, markdown 다운로드)


## 🚀 기술적 어필 포인트

1. **모델 스위칭 용이성**

   - `llm` 폴더를 구성하여 모델 클라이언트화
   - 서비스 및 모델명 기반으로 동적으로 클라이언트 교체 가능

2. **기능 확장성**

   - 에이전트 추가 시, 인텐트 라우터, 그래프 추가하여 쉽게 적용 가능
   - 신규 기능 추가 시 에이전트만 구현하면 즉시 적용 가능

3. **효율적 인텐트 라우팅**

   - 초기 대화 진입 시에만 LLM 인텐트 판단 실행
   - 특정 에이전트 진입 후에는 불필요한 추가 판단 생략

4. **LLM 활용 고도화**

   - 상대적 시간(`today`) 정보를 프롬프트에 제공하여 정확한 일정 계산
   - Structured Output을 활용해 파싱 에러 방지 및 완성도 높은 슬롯 필링 구현
   - Google Places API 쿼리 성능 향상을 위해 LLM으로 자연어 쿼리 정제


## 🛠️ 기술 스택

- **LangChain & LangGraph**
- **Streamlit**
- **OpenAI GPT-4o API**
- **Google APIs (Places & Calendar)**

## 📁 프로젝트 구조

```
travel_agent
├── agents
│   ├── calendar_agent.py
│   ├── location_search_agent.py
│   ├── location_search_api_agent.py
│   ├── share_agent.py
│   ├── travel_plan_agent.py
│   └── travel_scehdule_agent.py
├── common
│   └── forms.py
├── config
│   └── config.py
├── graphs
│   ├── graph_state.py
│   └── main_graph.py
├── llm
│   ├── llm_client.py
│   └── openai
│       └── openai_client.py
├── prompts
│   └── prompts.py
├── pytest.ini
├── requirements.txt
├── services
│   ├── llm_judge.py
│   └── orchestrator.py
├── tests
│   ├── 01_test_llm_client.py
│   ├── 02_test_calendar_api.py
│   ├── 03_test_location_search_api.py
│   └── 04_test_share_tool.py
├── tools
│   ├── calendar_api.py
│   ├── location_search_api.py
│   └── share_tool.py
├── ui
│   └── app.py
├── itinerary_20250622_064736.md
└── README.md

```

## 🚩 설치 및 실행 방법

### 환경 변수 설정 (`.env`)

```dotenv
OPENAI_API_KEY=your_key
GOOGLE_PLACE_KEY=your_key
SERVICE_ACCOUNT_FILE=your_file.json
CALENDAR_ID=your_calendar_id
```

### 로컬 실행

```bash
# python 3.10
pip install -r requirements.txt
streamlit run frontend_app.py
```

## ✅ 단위 테스트

```bash
pytest tests/
```

## 📸 에이전트 대화 내역

별도 캡처 파일 참조 (`asset/` 디렉토리 내 포함)

---

## 📎 샘플 결과 파일

- [에이전트 대화 샘플 PDF 다운로드](./blob/main/asset/에이전트_대화_캡처.pdf)
   > 위 링크는 제출 시 함께 포함된 `asset/에이전트_대화_캡쳐.pdf` 파일을 참조합니다.
- [에이전트 여행 일정 공유 MD 다운로드](.blob/main/asset/여행일정_공유.md)
   > 위 링크는 제출 시 함께 포함된 `asset/여행일정_공유.md` 파일을 참조합니다.
---