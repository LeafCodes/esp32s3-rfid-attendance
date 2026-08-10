from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(8), unique=True, index=True, nullable=False)
    name = Column(String(64), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

    attendances = relationship("Attendance", back_populates="card")


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"))
    uid = Column(String(8), index=True, nullable=False)
    name = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(4), nullable=False)  # IN or OUT

    card = relationship("Card", back_populates="attendances")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
