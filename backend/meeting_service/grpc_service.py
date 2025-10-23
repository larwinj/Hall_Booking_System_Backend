import grpc
from concurrent import futures
import asyncio
from typing import Dict, Set
import queue
from datetime import datetime

from .models import MeetingStore
from .proto import meeting_pb2, meeting_pb2_grpc

class MeetingServicer(meeting_pb2_grpc.MeetingServiceServicer):
    def __init__(self):
        self.store = MeetingStore()
        self.message_queues: Dict[str, Set[queue.Queue]] = {}
        self.signal_queues: Dict[str, Dict[str, queue.Queue]] = {}
    
    def CreateMeeting(self, request, context):
        try:
            existing = self.store.get_meeting_by_name(request.meeting_name)
            if existing and existing.is_active:
                return meeting_pb2.MeetingResponse(
                    success=False,
                    message="Meeting with this name already exists"
                )
            
            meeting = self.store.create_meeting(
                meeting_name=request.meeting_name,
                host_id=request.host_id,
                host_name=request.host_name
            )
            
            self.message_queues[meeting.meeting_id] = set()
            self.signal_queues[meeting.meeting_id] = {}
            
            return meeting_pb2.MeetingResponse(
                success=True,
                message="Meeting created successfully",
                meeting_id=meeting.meeting_id,
                meeting_url=f"/{request.meeting_name}"
            )
        except Exception as e:
            return meeting_pb2.MeetingResponse(
                success=False,
                message=f"Error creating meeting: {str(e)}"
            )
    
    def JoinMeeting(self, request, context):
        try:
            meeting = self.store.get_meeting_by_name(request.meeting_name)
            
            if not meeting or not meeting.is_active:
                return meeting_pb2.JoinMeetingResponse(
                    success=False,
                    message="Meeting not found or has ended"
                )
            
            participant = self.store.add_participant(
                meeting=meeting,
                user_id=request.user_id,
                user_name=request.user_name
            )
            
            if meeting.meeting_id not in self.signal_queues:
                self.signal_queues[meeting.meeting_id] = {}
            self.signal_queues[meeting.meeting_id][request.user_id] = queue.Queue()
            
            participants = [
                meeting_pb2.Participant(
                    user_id=p.user_id,
                    user_name=p.user_name,
                    audio_enabled=p.audio_enabled,
                    video_enabled=p.video_enabled,
                    is_host=p.is_host
                )
                for p in meeting.participants.values()
            ]
            
            return meeting_pb2.JoinMeetingResponse(
                success=True,
                message="Joined meeting successfully",
                meeting_id=meeting.meeting_id,
                participants=participants
            )
        except Exception as e:
            return meeting_pb2.JoinMeetingResponse(
                success=False,
                message=f"Error joining meeting: {str(e)}"
            )
    
    def LeaveMeeting(self, request, context):
        try:
            meeting = self.store.get_meeting_by_id(request.meeting_id)
            if meeting:
                self.store.remove_participant(meeting, request.user_id)
                
                if request.meeting_id in self.signal_queues:
                    if request.user_id in self.signal_queues[request.meeting_id]:
                        del self.signal_queues[request.meeting_id][request.user_id]
                
                return meeting_pb2.StatusResponse(
                    success=True,
                    message="Left meeting successfully"
                )
            return meeting_pb2.StatusResponse(
                success=False,
                message="Meeting not found"
            )
        except Exception as e:
            return meeting_pb2.StatusResponse(
                success=False,
                message=f"Error leaving meeting: {str(e)}"
            )
    
    def SendMessage(self, request, context):
        try:
            meeting = self.store.get_meeting_by_id(request.meeting_id)
            if not meeting:
                return meeting_pb2.StatusResponse(
                    success=False,
                    message="Meeting not found"
                )
            
            msg = self.store.add_message(
                meeting=meeting,
                user_id=request.user_id,
                user_name=request.user_name,
                message=request.message
            )
            
            msg_response = meeting_pb2.MessageResponse(
                message_id=msg.message_id,
                user_id=msg.user_id,
                user_name=msg.user_name,
                message=msg.message,
                timestamp=msg.timestamp.isoformat()
            )
            
            if request.meeting_id in self.message_queues:
                for q in list(self.message_queues[request.meeting_id]):
                    try:
                        q.put_nowait(msg_response)
                    except:
                        self.message_queues[request.meeting_id].discard(q)
            
            return meeting_pb2.StatusResponse(
                success=True,
                message="Message sent successfully"
            )
        except Exception as e:
            return meeting_pb2.StatusResponse(
                success=False,
                message=f"Error sending message: {str(e)}"
            )
    
    def GetMessages(self, request, context):
        try:
            meeting = self.store.get_meeting_by_id(request.meeting_id)
            if not meeting:
                return meeting_pb2.MessageListResponse(messages=[])
            
            messages = [
                meeting_pb2.MessageResponse(
                    message_id=msg.message_id,
                    user_id=msg.user_id,
                    user_name=msg.user_name,
                    message=msg.message,
                    timestamp=msg.timestamp.isoformat()
                )
                for msg in meeting.messages
            ]
            
            return meeting_pb2.MessageListResponse(messages=messages)
        except Exception as e:
            return meeting_pb2.MessageListResponse(messages=[])
    
    def StreamMessages(self, request, context):
        meeting = self.store.get_meeting_by_id(request.meeting_id)
        if not meeting:
            return
        
        msg_queue = queue.Queue()
        
        if request.meeting_id not in self.message_queues:
            self.message_queues[request.meeting_id] = set()
        self.message_queues[request.meeting_id].add(msg_queue)
        
        try:
            while context.is_active():
                try:
                    msg = msg_queue.get(timeout=1)
                    yield msg
                except queue.Empty:
                    continue
        finally:
            if request.meeting_id in self.message_queues:
                self.message_queues[request.meeting_id].discard(msg_queue)
    
    def SendWebRTCSignal(self, request, context):
        try:
            meeting = self.store.get_meeting_by_id(request.meeting_id)
            if not meeting:
                return meeting_pb2.StatusResponse(
                    success=False,
                    message="Meeting not found"
                )
            
            signal = meeting_pb2.WebRTCSignalResponse(
                from_user_id=request.from_user_id,
                to_user_id=request.to_user_id,
                signal_type=request.signal_type,
                signal_data=request.signal_data
            )
            
            if request.meeting_id in self.signal_queues:
                if request.to_user_id in self.signal_queues[request.meeting_id]:
                    try:
                        self.signal_queues[request.meeting_id][request.to_user_id].put_nowait(signal)
                    except:
                        pass
            
            return meeting_pb2.StatusResponse(
                success=True,
                message="Signal sent successfully"
            )
        except Exception as e:
            return meeting_pb2.StatusResponse(
                success=False,
                message=f"Error sending signal: {str(e)}"
            )
    
    def StreamWebRTCSignals(self, request, context):
        meeting = self.store.get_meeting_by_id(request.meeting_id)
        if not meeting:
            return
        
        if request.meeting_id not in self.signal_queues:
            self.signal_queues[request.meeting_id] = {}
        
        if request.user_id not in self.signal_queues[request.meeting_id]:
            self.signal_queues[request.meeting_id][request.user_id] = queue.Queue()
        
        signal_queue = self.signal_queues[request.meeting_id][request.user_id]
        
        try:
            while context.is_active():
                try:
                    signal = signal_queue.get(timeout=1)
                    yield signal
                except queue.Empty:
                    continue
        finally:
            pass
    
    def UpdateParticipantStatus(self, request, context):
        try:
            meeting = self.store.get_meeting_by_id(request.meeting_id)
            if not meeting:
                return meeting_pb2.StatusResponse(
                    success=False,
                    message="Meeting not found"
                )
            
            self.store.update_participant_status(
                meeting=meeting,
                user_id=request.user_id,
                audio_enabled=request.audio_enabled,
                video_enabled=request.video_enabled
            )
            
            return meeting_pb2.StatusResponse(
                success=True,
                message="Status updated successfully"
            )
        except Exception as e:
            return meeting_pb2.StatusResponse(
                success=False,
                message=f"Error updating status: {str(e)}"
            )
    
    def GetParticipants(self, request, context):
        try:
            meeting = self.store.get_meeting_by_id(request.meeting_id)
            if not meeting:
                return meeting_pb2.ParticipantListResponse(participants=[])
            
            participants = [
                meeting_pb2.Participant(
                    user_id=p.user_id,
                    user_name=p.user_name,
                    audio_enabled=p.audio_enabled,
                    video_enabled=p.video_enabled,
                    is_host=p.is_host
                )
                for p in meeting.participants.values()
            ]
            
            return meeting_pb2.ParticipantListResponse(participants=participants)
        except Exception as e:
            return meeting_pb2.ParticipantListResponse(participants=[])
    
    def EndMeeting(self, request, context):
        try:
            meeting = self.store.get_meeting_by_id(request.meeting_id)
            if not meeting:
                return meeting_pb2.StatusResponse(
                    success=False,
                    message="Meeting not found"
                )
            
            if meeting.host_id != request.host_id:
                return meeting_pb2.StatusResponse(
                    success=False,
                    message="Only host can end the meeting"
                )
            
            self.store.end_meeting(request.meeting_id)
            
            if request.meeting_id in self.message_queues:
                del self.message_queues[request.meeting_id]
            if request.meeting_id in self.signal_queues:
                del self.signal_queues[request.meeting_id]
            
            return meeting_pb2.StatusResponse(
                success=True,
                message="Meeting ended successfully"
            )
        except Exception as e:
            return meeting_pb2.StatusResponse(
                success=False,
                message=f"Error ending meeting: {str(e)}"
            )