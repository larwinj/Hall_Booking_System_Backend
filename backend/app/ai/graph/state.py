from typing import TypedDict, Optional, List, Annotated
from operator import add


class SearchFilters(TypedDict, total=False):
    """Extracted search filters from user query"""
    city: Optional[str]
    capacity: Optional[int]
    room_type: Optional[str]
    min_rating: Optional[float]
    amenities: Optional[List[str]]
    max_rate: Optional[float]
    venue_name: Optional[str]


class ChatState(TypedDict, total=False):
    """State for the chat workflow"""
    # Input
    user_message: str
    session_id: str
    chat_history: List[dict]
    
    # Processing
    query_intent: str  # "search", "info", "greeting", "followup", etc.
    search_filters: SearchFilters
    is_followup: bool  # Whether this is a follow-up question
    previous_filters: SearchFilters  # Filters from previous query for context
    
    # Results
    rooms: List[dict]
    room_count: int
    
    # Output
    response_message: str
    has_room_results: bool
