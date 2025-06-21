import os
import pytest
import logging
from llm.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)

@pytest.mark.asyncio
async def test_classify_intent():
    client = LLMClient(service_name="openai", model_name="gpt-4o").get_client()
    message = "7월 1일에 제주도 여행 일정 좀 짜줘"

    intent = client.classify_intent(message)

    assert intent in ["calendar", "location_search", "share_itinerary", "travel_schedule", "unknown"]

    logging.info(f"Intent: {intent}")