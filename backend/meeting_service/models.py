from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
import uuid

@dataclass
class Participant:
    user_id: str
    user_name: str
    audio_enabled: bool = True
    video_enabled: bool = True
    is_host: bool = False
    joined_at: datetime = field(default_factory=datetime.now)

@dataclass
class Message:
    message_id: str
    user_id: str
    user_name: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Meeting:
    meeting_id: str
    meeting_name: str
    host_id: str
    host_name: str
    created_at: datetime = field(default_factory=datetime.now)
    participants: Dict[str, Participant] = field(default_factory=dict)
    messages: List[Message] = field(default_factory=list)
    is_active: bool = True

class MeetingStore:
    def __init__(self):
        self.meetings_by_id: Dict[str, Meeting] = {}
        self.meetings_by_name: Dict[str, Meeting] = {}
    
    def create_meeting(self, meeting_name: str, host_id: str, host_name: str) -> Meeting:
        meeting_id = str(uuid.uuid4())
        
        host_participant = Participant(
            user_id=host_id,
            user_name=host_name,
            is_host=True
        )
        
        meeting = Meeting(
            meeting_id=meeting_id,
            meeting_name=meeting_name,
            host_id=host_id,
            host_name=host_name,
            participants={host_id: host_participant}
        )
        
        self.meetings_by_id[meeting_id] = meeting
        self.meetings_by_name[meeting_name.lower()] = meeting
        return meeting
    
    def get_meeting_by_id(self, meeting_id: str) -> Meeting:
        return self.meetings_by_id.get(meeting_id)
    
    def get_meeting_by_name(self, meeting_name: str) -> Meeting:
        return self.meetings_by_name.get(meeting_name.lower())
    
    def add_participant(self, meeting: Meeting, user_id: str, user_name: str) -> Participant:
        participant = Participant(user_id=user_id, user_name=user_name)
        meeting.participants[user_id] = participant
        return participant
    
    def remove_participant(self, meeting: Meeting, user_id: str):
        if user_id in meeting.participants:
            del meeting.participants[user_id]
    
    def add_message(self, meeting: Meeting, user_id: str, user_name: str, message: str) -> Message:
        msg = Message(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            user_name=user_name,
            message=message
        )
        meeting.messages.append(msg)
        return msg
    
    def update_participant_status(self, meeting: Meeting, user_id: str, audio_enabled: bool, video_enabled: bool):
        if user_id in meeting.participants:
            meeting.participants[user_id].audio_enabled = audio_enabled
            meeting.participants[user_id].video_enabled = video_enabled
    
    def end_meeting(self, meeting_id: str):
        meeting = self.meetings_by_id.get(meeting_id)
        if meeting:
            meeting.is_active = False
            meeting_name = meeting.meeting_name.lower()
            if meeting_name in self.meetings_by_name:
                del self.meetings_by_name[meeting_name]