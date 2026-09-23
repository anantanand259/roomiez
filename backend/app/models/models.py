import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    COLLECTOR = "COLLECTOR"
    ADMIN = "ADMIN"

class RoomStatus(str, enum.Enum):
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    REJECTED = "REJECTED"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Owner(Base):
    __tablename__ = "owners"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    phone = Column(String)
    contact_notes = Column(Text)

class Room(Base):
    __tablename__ = "rooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    rent = Column(Float, nullable=False)
    security_deposit = Column(Float)
    max_occupants = Column(Integer)
    available_beds = Column(Integer)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    locality = Column(String)
    status = Column(Enum(RoomStatus), default=RoomStatus.PENDING_VERIFICATION)
    last_verified_at = Column(DateTime(timezone=True))
    collector_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("owners.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RoomPhoto(Base):
    __tablename__ = "room_photos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    cloudinary_url = Column(String)
    public_id = Column(String)
    sort_order = Column(Integer, default=0)

class RoomSubmission(Base):
    __tablename__ = "room_submissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collector_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    payload = Column(Text)
    status = Column(String, default="SUBMITTED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Verification(Base):
    __tablename__ = "verifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    result = Column(String)
    notes = Column(Text)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())

class Lead(Base):
    __tablename__ = "leads"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    status = Column(String, default="INTERESTED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    budget_min = Column(Float)
    budget_max = Column(Float)
    people = Column(Integer)
    preferred_area = Column(String)
    max_distance_km = Column(Float)
    bathroom_preference = Column(String)
    kitchen_preference = Column(String)
    furnished_preference = Column(String)
    move_in_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    rating = Column(Integer)
    issue = Column(String)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())