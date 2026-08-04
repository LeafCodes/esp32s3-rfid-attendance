from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CardCreate(BaseModel):
    uid: str
    name: str


class CardResponse(BaseModel):
    id: int
    uid: str
    name: str
    added_at: datetime
    active: bool

    class Config:
        from_attributes = True


class AttendanceCreate(BaseModel):
    uid: str
    name: str
    timestamp: str
    status: str  # IN or OUT


class AttendanceResponse(BaseModel):
    id: int
    card_id: int
    uid: str
    name: str
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True


class AttendanceLog(BaseModel):
    attendances: List[AttendanceResponse]
    total: int
