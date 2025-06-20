from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class PlanSchema(BaseModel):
    itinerary: str
    final_confirm: str
    message: str
    
class LocationSchema(BaseModel):
    region: str
    selected_place: str
    detail_search: str
    message: str
    
class ReservationSchema(BaseModel):
    departure: str
    arrival: str
    start_date: str
    end_date: str
    message: str