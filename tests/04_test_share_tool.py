import os
import re
import pytest
import glob
from tools.share_tool import generate_itinerary_pdf, generate_shareable_link

@pytest.fixture
def sample_itinerary():
    return (
        "### 2025-07-01 (Day 1):\n"
        "- **오전:** 서울 출발 및 도착지 도착\n"
        "- **오후:** 관광지 A 방문\n"
        "- **저녁:** 현지 음식 체험\n"
    )


def test_generate_itinerary_pdf_creates_file(sample_itinerary, tmp_path, monkeypatch):
    # 현재 작업 디렉터리를 임시 디렉터리로 변경
    monkeypatch.chdir(tmp_path)

    response = generate_itinerary_pdf(sample_itinerary)
    # 응답 메시지 확인
    assert "PDF 파일로 여행 일정을 다운로드 했습니다" in response

    # 생성된 파일 패턴 확인
    pdf_files = glob.glob(str(tmp_path / "itinerary_*.pdf"))
    assert len(pdf_files) == 1, f"PDF 파일이 생성되지 않았습니다: {pdf_files}"


def test_generate_shareable_link_creates_file_and_returns_path(sample_itinerary, tmp_path, monkeypatch):
    # 현재 작업 디렉터리를 임시 디렉터리로 변경
    monkeypatch.chdir(tmp_path)

    result = generate_shareable_link(sample_itinerary)
    # 응답 메시 확인
    assert "link를 만들어드렸습니다" in result

    # file:// 경로 추출
    match = re.search(r'file://(.+\.md)', result)
    assert match, f"file:// 경로가 포함되지 않았습니다: {result}"
    file_path = match.group(1)

    assert os.path.exists(file_path), f"md 파일이 생성되지 않았습니다: {file_path}"