"""
AI Schemas
Request and response models for AI chat endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class RoomResult(BaseModel):
    """Room result in chat response"""
    id: int
    name: str
    venue_id: int
    venue_name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    capacity: int
    rate_per_hour: float
    type: str
    amenities: List[str] = []
    description: Optional[str] = None
    room_images: List[str] = []
    status: bool = True
    average_rating: float = 0.0


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="AI response message")
    rooms: Optional[List[RoomResult]] = Field(None, description="Filtered rooms to display")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    has_room_results: bool = Field(False, description="Whether rooms are included in response")


class ClearSessionResponse(BaseModel):
    """Response for session clear endpoint"""
    success: bool
    message: str
