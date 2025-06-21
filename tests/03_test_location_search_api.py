from tools.location_search_api import search_places

def test_search_places():
    results = search_places("오사카 맛집")
    print(results)
    assert isinstance(results, list), "결과가 리스트 형식이 아닙니다"
    assert results, "검색 결과가 비어 있습니다"
    for place in results:
        assert 'name' in place and 'rating' in place and 'formatted_address' in place, "검색 결과 항목에 필요한 키가 없습니다"
