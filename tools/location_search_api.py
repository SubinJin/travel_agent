import os
import requests
from config.config import GOOGLE_PLACE_KEY

def search_places(search_query: str) -> list[dict]:
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": search_query,
        "key": GOOGLE_PLACE_KEY,
        "language": "ko"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()               # HTTP 오류가 있으면 예외 발생
    data = resp.json()

    # 필터링
    filtered = [
        {
            "name": item.get("name"),
            "rating": item.get("rating"),
            "formatted_address": item.get("formatted_address"),
        }
        for item in data.get("results", [])
    ]
    return filtered