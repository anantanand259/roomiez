from pydantic import BaseModel
from typing import Optional
from typing import List
from datetime import datetime


class RoomSubmissionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    rent: float
    max_occupants: Optional[int] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    locality: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None

class RoomSubmissionResponse(BaseModel):
    id: str
    status: str
    message: str

class RoomSubmissionOut(BaseModel):
    id: str
    status: str
    payload: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApprovalResponse(BaseModel):
    room_id: str
    status: str
    message: str

class RoomOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    rent: float
    max_occupants: Optional[int] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    locality: Optional[str] = None
    status: str
    last_verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LeadCreate(BaseModel):
    student_id: Optional[str] = None
    message: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    room_id: str
    status: str
    message: str

class RoomStatusUpdateResponse(BaseModel):
    room_id: str
    status: str
    message: str