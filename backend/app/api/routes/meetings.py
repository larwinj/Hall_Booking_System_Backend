from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.db.session import AsyncSession, get_db
from pydantic import BaseModel

router = APIRouter(prefix="/meeting", tags=["MeetingURL"])

class MeetingLinkResponse(BaseModel):
    meeting_link: str
    message: str = "Click the link to join the meeting in a new tab"

@router.get("/getlink", response_model=MeetingLinkResponse, description="Access by venue owner only.")
async def get_meeting_link(db: AsyncSession = Depends(get_db)):
    meeting_link = "http://127.0.0.1:8080/"
    
    return {
        "meeting_link": meeting_link,
        "message": "Click the link to join the meeting in a new tab"
    }