import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ai import ChatRequest, ChatResponse, ClearSessionResponse, RoomResult
from app.ai.memory.session_memory import session_manager
from app.ai.graph.graph import process_chat_message
from app.ai.config import get_ai_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process a natural language chat query about rooms/venues.
    
    Returns:
    - message: AI response text
    - rooms: List of matching rooms (if search query)
    - session_id: Session ID for conversation continuity
    - has_room_results: Whether rooms were found
    
    Example queries:
    - "I need rooms in Coimbatore with good reviews"
    - "Show me conference rooms for 15 members"
    - "I need a party hall in Madurai"
    """
    try:
        # Get or create session
        session = session_manager.get_or_create_session(request.session_id)
        session_id = session.session_id
        
        # Get chat history
        chat_history = session.get_history(max_messages=10)
        
        # Get previous filters from context
        previous_filters = session.context.get("last_filters", {})
        
        # Add user message to history
        session.add_message("user", request.message)
        
        # Process through AI workflow
        result = await process_chat_message(
            user_message=request.message,
            session_id=session_id,
            chat_history=chat_history,
            previous_filters=previous_filters,
            db=db
        )
        
        # Store the current filters for follow-up questions
        if result.get("search_filters"):
            session.update_context("last_filters", result["search_filters"])
        
        # Add assistant response to history
        session.add_message("assistant", result["response_message"])
        
        # Convert rooms to response model
        rooms = None
        if result.get("rooms"):
            rooms = [RoomResult(**room) for room in result["rooms"]]
        
        return ChatResponse(
            message=result["response_message"],
            rooms=rooms,
            session_id=session_id,
            has_room_results=result.get("has_room_results", False)
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred processing your request: {str(e)}"
        )


@router.delete("/chat/{session_id}", response_model=ClearSessionResponse)
async def clear_chat_session(session_id: str):
    """
    Clear a chat session and its memory.
    
    This removes all conversation history for the given session.
    """
    try:
        deleted = session_manager.delete_session(session_id)
        if deleted:
            return ClearSessionResponse(
                success=True,
                message="Session cleared successfully"
            )
        else:
            return ClearSessionResponse(
                success=False,
                message="Session not found or already expired"
            )
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear session"
        )


@router.get("/health")
async def ai_health_check():
    """Check if AI service is configured properly"""
    settings = get_ai_settings()
    return {
        "status": "ok",
        "model": settings.ai_model,
        "api_configured": bool(settings.groq_api_key)
    }
