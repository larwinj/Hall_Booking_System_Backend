from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
import grpc
import uuid
import json
import asyncio
from datetime import datetime

from .proto import meeting_pb2, meeting_pb2_grpc

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# gRPC client connection
def get_grpc_stub():
    channel = grpc.insecure_channel('localhost:50051')
    return meeting_pb2_grpc.MeetingServiceStub(channel)

# Pydantic models
class CreateMeetingRequest(BaseModel):
    meeting_name: str
    host_name: str

class JoinMeetingRequest(BaseModel):
    user_name: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, meeting_id: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = {}
        self.active_connections[meeting_id][user_id] = websocket
    
    def disconnect(self, meeting_id: str, user_id: str):
        if meeting_id in self.active_connections:
            if user_id in self.active_connections[meeting_id]:
                del self.active_connections[meeting_id][user_id]
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]
    
    async def send_personal_message(self, message: dict, meeting_id: str, user_id: str):
        if meeting_id in self.active_connections:
            if user_id in self.active_connections[meeting_id]:
                try:
                    await self.active_connections[meeting_id][user_id].send_json(message)
                except:
                    pass
    
    async def broadcast(self, message: dict, meeting_id: str, exclude_user: Optional[str] = None):
        if meeting_id in self.active_connections:
            for user_id, connection in list(self.active_connections[meeting_id].items()):
                if exclude_user and user_id == exclude_user:
                    continue
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# Routes
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/create", response_class=HTMLResponse)
async def create_meeting_page(request: Request):
    return templates.TemplateResponse("create_meeting.html", {"request": request})

@router.post("/api/meeting/create")
async def create_meeting(req: CreateMeetingRequest):
    try:
        stub = get_grpc_stub()
        host_id = str(uuid.uuid4())
        
        response = stub.CreateMeeting(
            meeting_pb2.CreateMeetingRequest(
                meeting_name=req.meeting_name,
                host_id=host_id,
                host_name=req.host_name
            )
        )
        
        if response.success:
            return {
                "success": True,
                "meeting_id": response.meeting_id,
                "meeting_url": response.meeting_url,
                "host_id": host_id,
                "message": response.message
            }
        else:
            raise HTTPException(status_code=400, detail=response.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{meeting_name}", response_class=HTMLResponse)
async def join_meeting_page(request: Request, meeting_name: str):
    return templates.TemplateResponse("meeting.html", {
        "request": request,
        "meeting_name": meeting_name
    })

@router.post("/api/meeting/{meeting_name}/join")
async def join_meeting(meeting_name: str, req: JoinMeetingRequest):
    try:
        stub = get_grpc_stub()
        user_id = str(uuid.uuid4())
        
        response = stub.JoinMeeting(
            meeting_pb2.JoinMeetingRequest(
                meeting_name=meeting_name,
                user_id=user_id,
                user_name=req.user_name
            )
        )
        
        if response.success:
            participants = [
                {
                    "user_id": p.user_id,
                    "user_name": p.user_name,
                    "audio_enabled": p.audio_enabled,
                    "video_enabled": p.video_enabled,
                    "is_host": p.is_host
                }
                for p in response.participants
            ]
            
            return {
                "success": True,
                "meeting_id": response.meeting_id,
                "user_id": user_id,
                "participants": participants,
                "message": response.message
            }
        else:
            raise HTTPException(status_code=404, detail=response.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{meeting_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str, user_id: str):
    await manager.connect(meeting_id, user_id, websocket)
    stub = get_grpc_stub()
    
    try:
        # Notify others that user joined
        await manager.broadcast(
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            },
            meeting_id,
            exclude_user=user_id
        )
        
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "chat_message":
                # Send message via gRPC
                stub.SendMessage(
                    meeting_pb2.MessageRequest(
                        meeting_id=meeting_id,
                        user_id=user_id,
                        user_name=data.get("user_name"),
                        message=data.get("message")
                    )
                )
                
                # Broadcast to all participants
                await manager.broadcast(
                    {
                        "type": "chat_message",
                        "user_id": user_id,
                        "user_name": data.get("user_name"),
                        "message": data.get("message"),
                        "timestamp": datetime.now().isoformat()
                    },
                    meeting_id
                )
            
            elif message_type == "webrtc_signal":
                # Send WebRTC signal via gRPC
                stub.SendWebRTCSignal(
                    meeting_pb2.WebRTCSignalRequest(
                        meeting_id=meeting_id,
                        from_user_id=user_id,
                        to_user_id=data.get("to_user_id"),
                        signal_type=data.get("signal_type"),
                        signal_data=json.dumps(data.get("signal_data"))
                    )
                )
                
                # Send directly to target user
                await manager.send_personal_message(
                    {
                        "type": "webrtc_signal",
                        "from_user_id": user_id,
                        "signal_type": data.get("signal_type"),
                        "signal_data": data.get("signal_data")
                    },
                    meeting_id,
                    data.get("to_user_id")
                )
            
            elif message_type == "status_update":
                # Update participant status via gRPC
                stub.UpdateParticipantStatus(
                    meeting_pb2.ParticipantStatusRequest(
                        meeting_id=meeting_id,
                        user_id=user_id,
                        audio_enabled=data.get("audio_enabled"),
                        video_enabled=data.get("video_enabled")
                    )
                )
                
                # Broadcast status update
                await manager.broadcast(
                    {
                        "type": "status_update",
                        "user_id": user_id,
                        "audio_enabled": data.get("audio_enabled"),
                        "video_enabled": data.get("video_enabled")
                    },
                    meeting_id
                )
            
            elif message_type == "end_meeting":
                # End meeting via gRPC
                response = stub.EndMeeting(
                    meeting_pb2.EndMeetingRequest(
                        meeting_id=meeting_id,
                        host_id=user_id
                    )
                )
                
                if response.success:
                    # Notify all participants
                    await manager.broadcast(
                        {
                            "type": "meeting_ended",
                            "message": "Meeting has been ended by the host"
                        },
                        meeting_id
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(meeting_id, user_id)
        
        # Leave meeting via gRPC
        stub.LeaveMeeting(
            meeting_pb2.LeaveMeetingRequest(
                meeting_id=meeting_id,
                user_id=user_id
            )
        )
        
        # Notify others
        await manager.broadcast(
            {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            },
            meeting_id
        )

@router.get("/api/meeting/{meeting_id}/messages")
async def get_messages(meeting_id: str):
    try:
        stub = get_grpc_stub()
        response = stub.GetMessages(
            meeting_pb2.GetMessagesRequest(meeting_id=meeting_id)
        )
        
        messages = [
            {
                "message_id": msg.message_id,
                "user_id": msg.user_id,
                "user_name": msg.user_name,
                "message": msg.message,
                "timestamp": msg.timestamp
            }
            for msg in response.messages
        ]
        
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/meeting/{meeting_id}/participants")
async def get_participants(meeting_id: str):
    try:
        stub = get_grpc_stub()
        response = stub.GetParticipants(
            meeting_pb2.GetParticipantsRequest(meeting_id=meeting_id)
        )
        
        participants = [
            {
                "user_id": p.user_id,
                "user_name": p.user_name,
                "audio_enabled": p.audio_enabled,
                "video_enabled": p.video_enabled,
                "is_host": p.is_host
            }
            for p in response.participants
        ]
        
        return {"participants": participants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Provide a MeetingService symbol for backward compatibility with imports that expect it.
# This is a lightweight stub so existing imports (from .service import MeetingService)
# do not raise ImportError; replace with the real implementation if needed.
class MeetingService:
    """Stub MeetingService exported for backward compatibility."""
    pass