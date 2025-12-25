import json
import logging
import random
import re
from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.ai.graph.state import ChatState, SearchFilters
from app.ai.config import get_ai_settings
from app.ai.tools.room_search_tool import search_rooms_by_criteria

try:
    from langchain_groq import ChatGroq
except ImportError:
    from langchain_community.chat_models import ChatGroq

logger = logging.getLogger(__name__)

# System prompt for query parsing
QUERY_PARSER_PROMPT = """You are an AI assistant for a hall booking system. Your job is to understand user queries about room/venue bookings and extract search parameters.

Given a user message, analyze it and respond with a JSON object containing:
{
    "intent": "search" | "info" | "greeting" | "followup" | "other",
    "filters": {
        "city": "city name or null",
        "capacity": "number or null",
        "room_type": "Party Hall | Conference Room | Banquet Hall | Meeting Room or null",
        "min_rating": "number 1-5 or null if user mentions 'good reviews' use 4.0",
        "amenities": ["list of amenities"] or null,
        "max_rate": "max price per hour or null",
        "venue_name": "venue name or null"
    },
    "is_followup": true/false (if referring to previous results like 'show cheaper' or 'something bigger'),
    "response_hint": "brief suggestion for response if no search needed"
}

Examples:
- "I need rooms in Coimbatore with good reviews" → intent: "search", city: "Coimbatore", min_rating: 4.0
- "Show me conference rooms for 15 members" → intent: "search", room_type: "Conference Room", capacity: 15
- "I need rooms in Madurai for 15 members with good reviews" → intent: "search", city: "Madurai", capacity: 15, min_rating: 4.0
- "Something cheaper" → intent: "followup", is_followup: true
- "Hello" → intent: "greeting"
- "Show me party halls with WiFi" → intent: "search", room_type: "Party Hall", amenities: ["WiFi"]

Current conversation context will be provided. Use it to understand follow-up questions.
Respond ONLY with the JSON object, no other text."""


RESPONSE_GENERATOR_PROMPT = """You are a friendly AI assistant for a hall booking system. Generate a helpful, conversational response based on the search results.

Guidelines:
- Be concise and helpful
- If rooms were found, briefly summarize what was found (don't list all details, just key points)
- If no rooms found, suggest alternatives or ask for different criteria
- For greetings, respond warmly and offer to help find rooms
- Keep responses under 100 words
- Be encouraging about the available options

Context:
- User asked: {user_message}
- Rooms found: {room_count}
- Search filters used: {filters}

Generate a natural, helpful response."""


def get_llm():
    settings = get_ai_settings()
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.ai_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens
    )


async def parse_query_node(state: ChatState) -> ChatState:
    """Parse user query to extract intent and search filters"""
    llm = get_llm()
    
    # Build context from chat history
    history_context = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-6:]  # Last 3 exchanges
        history_context = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in recent
        ])
    
    # Include previous filters for followup context
    prev_filters_context = ""
    if state.get("previous_filters"):
        prev_filters_context = f"\nPrevious search filters: {json.dumps(state['previous_filters'])}"
    
    messages = [
        {"role": "system", "content": QUERY_PARSER_PROMPT},
        {"role": "user", "content": f"""Conversation history:
{history_context}

{prev_filters_context}

Current user message: {state['user_message']}

Extract the intent and filters as JSON."""}
    ]
    
    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        
        logger.info(f"Raw LLM response: {content[:500]}")  # Debug log
        
        # Handle Qwen model's chain-of-thought tags (like <think>...</think>)
        import re
        
        # Remove thinking tags if present
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        content = re.sub(r'<reasoning>.*?</reasoning>', '', content, flags=re.DOTALL)
        content = content.strip()
        
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)
        
        # Clean up response - remove markdown code blocks if present
        if "```" in content:
            # Extract content between code blocks
            parts = content.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    content = part
                    break
        
        content = content.strip()
        
        logger.info(f"Cleaned content for parsing: {content[:300]}")  # Debug log
        
        # If content is empty or doesn't look like JSON, use fallback
        if not content or not content.startswith("{"):
            logger.warning("Content doesn't start with {, using keyword extraction fallback")
            return await _fallback_keyword_extraction(state)
        
        parsed = json.loads(content)
        
        # Extract filters
        filters = parsed.get("filters", {})
        search_filters: SearchFilters = {}
        
        if filters.get("city") and filters.get("city") != "null":
            search_filters["city"] = str(filters["city"])
        if filters.get("capacity") and filters.get("capacity") != "null":
            search_filters["capacity"] = int(filters["capacity"])
        if filters.get("room_type") and filters.get("room_type") != "null":
            search_filters["room_type"] = str(filters["room_type"])
        if filters.get("min_rating") and filters.get("min_rating") != "null":
            search_filters["min_rating"] = float(filters["min_rating"])
        if filters.get("amenities") and filters.get("amenities") != "null":
            search_filters["amenities"] = filters["amenities"]
        if filters.get("max_rate") and filters.get("max_rate") != "null":
            search_filters["max_rate"] = float(filters["max_rate"])
        if filters.get("venue_name") and filters.get("venue_name") != "null":
            search_filters["venue_name"] = str(filters["venue_name"])
        
        # Handle followup - merge with previous filters
        is_followup = parsed.get("is_followup", False)
        if is_followup and state.get("previous_filters"):
            merged_filters = {**state["previous_filters"], **search_filters}
            search_filters = merged_filters
        
        return {
            **state,
            "query_intent": parsed.get("intent", "search"),
            "search_filters": search_filters,
            "is_followup": is_followup
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return await _fallback_keyword_extraction(state)
    except Exception as e:
        logger.error(f"Error parsing query: {e}")
        return await _fallback_keyword_extraction(state)


async def _fallback_keyword_extraction(state: ChatState) -> ChatState:
    """Fallback: Extract search parameters using simple keyword matching"""
    user_message = state.get("user_message", "").lower()
    search_filters: SearchFilters = {}
    
    # Common Indian cities for venue booking
    cities = ["coimbatore", "chennai", "madurai", "bangalore", "bengaluru", 
              "mumbai", "delhi", "hyderabad", "pune", "kolkata", "salem", 
              "trichy", "tiruchirappalli", "erode", "tirupur"]
    
    for city in cities:
        if city in user_message:
            search_filters["city"] = city.title()
            break
    
    # Room types
    room_types = {
        "party hall": "Party Hall",
        "conference room": "Conference Room", 
        "banquet hall": "Banquet Hall",
        "meeting room": "Meeting Room",
        "party": "Party Hall",
        "conference": "Conference Room",
        "banquet": "Banquet Hall",
        "meeting": "Meeting Room"
    }
    
    for keyword, room_type in room_types.items():
        if keyword in user_message:
            search_filters["room_type"] = room_type
            break
    
    # Capacity extraction
    import re
    capacity_patterns = [
        r'(\d+)\s*(?:people|persons|members|guests|pax)',
        r'for\s*(\d+)',
        r'capacity\s*(?:of\s*)?(\d+)'
    ]
    
    for pattern in capacity_patterns:
        match = re.search(pattern, user_message)
        if match:
            search_filters["capacity"] = int(match.group(1))
            break
    
    # Good reviews = min rating 4.0
    if "good review" in user_message or "good rating" in user_message or "highly rated" in user_message:
        search_filters["min_rating"] = 4.0
    
    # Info patterns - asking about the application itself
    info_patterns = [
        "tell about", "about this", "what is this", "what can you do",
        "help me", "how does this work", "what do you do", "your purpose",
        "this application", "this app", "this bot", "what are you"
    ]
    is_info_query = any(pattern in user_message for pattern in info_patterns)
    
    # Greeting patterns
    greeting_patterns = [
        "hi ", "hi,", "hello", "hey ", "hey,", "good morning", "good afternoon", "good evening",
        "howdy", "greetings", "namaste", "hola", "what's up", "whats up",
        "how are you", "nice to meet"
    ]
    # Check if message starts with greeting or contains only greeting
    is_greeting = any(user_message.startswith(greet) or user_message == greet.strip() for greet in greeting_patterns)
    if not is_greeting:
        is_greeting = user_message in ["hi", "hey", "hello"]
    
    # Check if asking about room count/stats
    count_patterns = ["how many", "total number", "count of", "number of"]
    is_count_query = any(pattern in user_message for pattern in count_patterns)
    
    # Determine intent
    if is_info_query:
        intent = "info"
    elif is_greeting and not search_filters and not is_count_query:
        intent = "greeting"
    elif is_count_query and "room" in user_message:
        # User is asking how many rooms - do a search with no filters to get all
        intent = "count"
    elif search_filters:
        intent = "search"
    else:
        # Check if it's related to venues/rooms at all
        venue_keywords = [
            "room", "hall", "venue", "book", "booking", "event", "function",
            "wedding", "birthday", "corporate", "seminar", "workshop",
            "capacity", "price", "rate", "available", "cheap", "affordable",
            "best", "top", "review", "rating", "amenity", "amenities",
            "wifi", "parking", "ac", "projector", "show", "find", "search",
            "list", "all", "need", "want", "looking"
        ]
        is_venue_related = any(keyword in user_message for keyword in venue_keywords)
        intent = "search" if is_venue_related else "off_topic"
    
    logger.info(f"Fallback extraction: intent={intent}, filters={search_filters}")
    
    return {
        **state,
        "query_intent": intent,
        "search_filters": search_filters,
        "is_followup": False
    }


async def search_rooms_node(state: ChatState, db) -> ChatState:
    """Search rooms based on extracted filters"""
    intent = state.get("query_intent")
    
    # Skip search for non-search intents (except count which needs all rooms)
    if intent not in ["search", "followup", "count"]:
        return {
            **state,
            "rooms": [],
            "room_count": 0,
            "has_room_results": False
        }
    
    filters = state.get("search_filters", {})
    
    try:
        rooms = await search_rooms_by_criteria(
            db=db,
            city=filters.get("city"),
            capacity=filters.get("capacity"),
            room_type=filters.get("room_type"),
            min_rating=filters.get("min_rating"),
            amenities=filters.get("amenities"),
            max_rate=filters.get("max_rate"),
            venue_name=filters.get("venue_name")
        )
        
        return {
            **state,
            "rooms": rooms,
            "room_count": len(rooms),
            "has_room_results": len(rooms) > 0
        }
        
    except Exception as e:
        logger.error(f"Error searching rooms: {e}")
        return {
            **state,
            "rooms": [],
            "room_count": 0,
            "has_room_results": False
        }


async def generate_response_node(state: ChatState) -> ChatState:
    """Generate natural language response"""
    try:
        llm = get_llm()
        
        intent = state.get("query_intent", "other")
        rooms = state.get("rooms", [])
        room_count = state.get("room_count", 0)
        filters = state.get("search_filters", {})
        user_message = state.get("user_message", "")
        
        logger.info(f"Generating response for intent: {intent}, room_count: {room_count}")
        
        response = ""
        
        # Build response based on intent
        if intent == "greeting":
            greetings = [
                "Hello! 👋 Welcome to the Hall Booking Assistant! I'm here to help you find the perfect venue for your event. Just tell me what you're looking for!",
                "Hi there! 😊 Looking for a venue? I can help you find conference rooms, party halls, banquet halls, and more. What kind of space do you need?",
                "Hey! 👋 Great to have you here! Tell me about your event - I'll find the best rooms for you. Try asking 'Show me party halls in Chennai' or 'I need a conference room for 20 people'."
            ]
            response = random.choice(greetings)
        
        elif intent == "info":
            # User is asking about the application
            response = """🏢 **Welcome to Hall Booking Assistant!**

I'm an AI-powered assistant designed to help you find the perfect venue for your events.

**What I can do:**
• Search rooms by **city** (Chennai, Coimbatore, Madurai, etc.)
• Filter by **capacity** (e.g., "room for 50 people")
• Find specific **room types** (Conference Room, Party Hall, Banquet Hall)
• Show venues with **good reviews** (rated 4+ stars)
• Help with **follow-up questions** ("Show something cheaper")

**Try asking:**
• "Show me party halls in Coimbatore"
• "I need a conference room for 20 people"
• "Find halls with good reviews"

How can I help you today?"""
        
        elif intent == "count":
            # User is asking how many rooms
            total = room_count if room_count > 0 else len(rooms)
            response = f"📊 We currently have **{total} rooms** available across various venues!\n\nWould you like me to show you rooms in a specific city or filter by capacity/type?"
        
        elif intent == "off_topic":
            # Politely redirect to venue-related queries
            response = "I appreciate your message, but I'm specifically designed to help you find and book venues! 🏢\n\nI can help you with:\n• Finding rooms by city (e.g., 'Show me halls in Coimbatore')\n• Searching by capacity (e.g., 'I need a room for 50 people')\n• Filtering by type (e.g., 'Find conference rooms')\n• Checking reviews (e.g., 'Halls with good reviews')\n\nHow can I help you find the perfect venue?"
        
        elif intent in ["search", "followup"]:
            if room_count > 0:
                # Build a summary of results
                cities = list(set(r.get("city", "") for r in rooms if r.get("city")))
                types = list(set(r.get("type", "") for r in rooms if r.get("type")))
                
                prompt = RESPONSE_GENERATOR_PROMPT.format(
                    user_message=user_message,
                    room_count=room_count,
                    filters=json.dumps(filters)
                )
                
                messages = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Found {room_count} rooms. Cities: {cities}. Types: {types}. Generate a brief, helpful response."}
                ]
                
                try:
                    result = await llm.ainvoke(messages)
                    response = result.content.strip()
                    # Remove any thinking tags from response
                    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
                except Exception as e:
                    logger.error(f"LLM invoke error in response gen: {e}")
                    response = f"Great news! 🎉 I found {room_count} rooms matching your criteria. The results are now displayed on the page. Would you like to refine your search?"
            else:
                # No results
                response = "I couldn't find any rooms matching your exact criteria. 😔\n\nTry adjusting your search:\n• Different city\n• Smaller capacity\n• Different room type\n\nOr just tell me what you need, and I'll do my best to help!"
        
        else:
            # Fallback for any other intent
            response = "I'm here to help you find the perfect venue! 🏢\n\nYou can ask me things like:\n• 'Show me rooms in Chennai'\n• 'I need a conference room for 20 people'\n• 'Find party halls with good reviews'\n• 'What's available in Coimbatore?'"

        logger.info(f"Final generated response (first 100 chars): {response[:100]}")
        
        return {
            **state,
            "response_message": response or "I'm ready to help you find a venue! What are you looking for?"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_response_node: {e}")
        return {
            **state,
            "response_message": "I'm sorry, I encountered an error while generating a response. But don't worry, I can still help you find a venue! What are you looking for?"
        }



def create_chat_workflow():
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("generate_response", generate_response_node)
    
    # Define edges
    workflow.add_edge(START, "parse_query")
    workflow.add_edge("parse_query", "generate_response")
    workflow.add_edge("generate_response", END)
    
    return workflow.compile()


# Note: search_rooms_node is called separately because it needs the db session
# The workflow handles query parsing and response generation
# The search is done in the route handler with the db session

async def process_chat_message(
    user_message: str,
    session_id: str,
    chat_history: list,
    previous_filters: dict,
    db
) -> dict:
    """
    Process a chat message through the workflow.
    Returns dict with response_message, rooms, has_room_results, search_filters
    """
    # Initial state
    state: ChatState = {
        "user_message": user_message,
        "session_id": session_id,
        "chat_history": chat_history,
        "previous_filters": previous_filters
    }
    
    # Step 1: Parse query
    state = await parse_query_node(state)
    
    # Step 2: Search rooms (if applicable)
    state = await search_rooms_node(state, db)
    
    # Step 3: Generate response
    state = await generate_response_node(state)
    
    return {
        "response_message": state.get("response_message", ""),
        "rooms": state.get("rooms", []),
        "has_room_results": state.get("has_room_results", False),
        "search_filters": state.get("search_filters", {}),
        "query_intent": state.get("query_intent", "other")
    }
