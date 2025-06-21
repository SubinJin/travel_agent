from pydantic import BaseModel

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
    
class CalendarCreateSchema(BaseModel) :
    summary: str
    location: str
    start_date: str
    end_date: str
    message : str
    
    
class CalendarReadSchema(BaseModel) :
    message : str
    
class CalendarUpdateSchema(BaseModel) :
    summary: str
    location: str
    start_date: str
    end_date: str
    event_id : str
    message : str
    
class CalendarDeleteSchema(BaseModel) :
    # summary: str
    event_id : str
    message : str
    
class ShareSchema(BaseModel) :
    message : str
    share_format : str
    