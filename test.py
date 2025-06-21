# demo_search.py
import os
from tools.location_search_api import search_places

# 1) 구글 API 키 환경변수 설정 확인
#    export GOOGLE_PLACE_KEY='여기에_발급받은_키를_넣으세요'

if __name__ == "__main__":
    query = "오사카 맛집"
    results = search_places(query)
    print(results)
    for idx, place in enumerate(results, start=1):
        print(f"{idx}. {place['name']} ({place.get('rating', 'N/A')}점)")
        print(f"   주소: {place['formatted_address']}\n")