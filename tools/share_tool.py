import logging
import os
from datetime import datetime

import markdown2
from weasyprint import HTML

def generate_itinerary_pdf(itinerary: str) -> str:
    base_dir = os.path.join(os.getcwd())
    os.makedirs(base_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"itinerary_{timestamp}.pdf"
    file_path = os.path.join(base_dir, file_name)
    
    # 마크다운을 HTML로 변환
    html = markdown2.markdown(itinerary)
    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"itinerary_{timestamp}.pdf"
    file_path = os.path.join(base_dir, file_name)

    # HTML을 PDF로 저장
    HTML(string=html).write_pdf(file_path)
    return "요청하신대로 PDF 파일로 여행 일정을 다운로드 했습니다!"

def generate_shareable_link(itinerary: str) -> str:
    base_dir = os.path.join(os.getcwd())
    os.makedirs(base_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"itinerary_{timestamp}.md"
    file_path = os.path.join(base_dir, file_name)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(itinerary)

    # 파일 URL 반환 (예: 로컬 파일 링크 혹은 CDN 업로드 후 URL)
    return f"요청하신대로 link를 만들어드렸습니다. 여행 일정을 공유해보세요! \nfile://{file_path}"