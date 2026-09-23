import json
import uuid
from typing import List
from app.schemas.room_schema import RoomSubmissionOut
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.room_schema import RoomSubmissionCreate, RoomSubmissionResponse
from app.models.models import RoomSubmission
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.models import Room, RoomStatus
from app.schemas.room_schema import ApprovalResponse
from typing import Optional
from app.schemas.room_schema import RoomOut
from app.models.models import Lead
from app.schemas.room_schema import LeadCreate, LeadResponse
from app.schemas.room_schema import RoomStatusUpdateResponse
from app.core.auth_deps import require_role
from app.schemas.room_schema import RejectionResponse

router = APIRouter()

@router.post("/rooms/submissions", response_model=RoomSubmissionResponse)
def create_room_submission(submission: RoomSubmissionCreate, db: Session = Depends(get_db)):
    new_submission = RoomSubmission(
        id=uuid.uuid4(),
        collector_id=None,  # will be set from auth later
        payload=json.dumps(submission.dict()),
        status="SUBMITTED"
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return RoomSubmissionResponse(
        id=str(new_submission.id),
        status=new_submission.status,
        message="Room submission received successfully"
    )

@router.get("/admin/submissions", response_model=List[RoomSubmissionOut])
def get_all_submissions(db: Session = Depends(get_db), current_user = Depends(require_role("ADMIN"))):
    submissions = db.query(RoomSubmission).all()
    result = []
    for s in submissions:
        result.append(RoomSubmissionOut(
            id=str(s.id),
            status=s.status,
            payload=s.payload,
            created_at=s.created_at
        ))
    return result


@router.post("/admin/submissions/{submission_id}/approve", response_model=ApprovalResponse)
def approve_submission(submission_id: str, db: Session = Depends(get_db), current_user = Depends(require_role("ADMIN"))):
    submission = db.query(RoomSubmission).filter(RoomSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.status == "APPROVED":
        raise HTTPException(status_code=409, detail="Submission already approved")

    payload = json.loads(submission.payload)

    new_room = Room(
        id=uuid.uuid4(),
        title=payload.get("title"),
        description=payload.get("description"),
        rent=payload.get("rent"),
        max_occupants=payload.get("max_occupants"),
        address=payload.get("address"),
        latitude=payload.get("latitude"),
        longitude=payload.get("longitude"),
        locality=payload.get("locality"),
        status=RoomStatus.ACTIVE,
        last_verified_at=datetime.now(timezone.utc),
        collector_id=submission.collector_id
    )
    db.add(new_room)

    submission.status = "APPROVED"

    db.commit()
    db.refresh(new_room)

    return ApprovalResponse(
        room_id=str(new_room.id),
        status="ACTIVE",
        message="Room approved and published successfully"
    )

@router.get("/rooms", response_model=List[RoomOut])
def search_rooms(
    min_rent: Optional[float] = None,
    max_rent: Optional[float] = None,
    locality: Optional[str] = None,
    max_occupants: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Room).filter(Room.status == RoomStatus.ACTIVE)

    if min_rent is not None:
        query = query.filter(Room.rent >= min_rent)
    if max_rent is not None:
        query = query.filter(Room.rent <= max_rent)
    if locality is not None:
        query = query.filter(Room.locality.ilike(f"%{locality}%"))
    if max_occupants is not None:
        query = query.filter(Room.max_occupants <= max_occupants)

    rooms = query.all()

    result = []
    for r in rooms:
        result.append(RoomOut(
            id=str(r.id),
            title=r.title,
            description=r.description,
            rent=r.rent,
            max_occupants=r.max_occupants,
            address=r.address,
            latitude=r.latitude,
            longitude=r.longitude,
            locality=r.locality,
            status=r.status.value if hasattr(r.status, "value") else r.status,
            last_verified_at=r.last_verified_at
        ))
    return result

@router.post("/rooms/{room_id}/lead", response_model=LeadResponse)
def create_lead(room_id: str, lead: LeadCreate, db: Session = Depends(get_db)):
    room_id = room_id.strip()
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    new_lead = Lead(
        id=uuid.uuid4(),
        student_id=lead.student_id,
        room_id=room.id,
        status="INTERESTED"
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return LeadResponse(
        id=str(new_lead.id),
        room_id=str(room.id),
        status=new_lead.status,
        message="Interest recorded successfully"
    )

@router.patch("/admin/rooms/{room_id}/deactivate", response_model=RoomStatusUpdateResponse)
def deactivate_room(room_id: str, db: Session = Depends(get_db), current_user = Depends(require_role("ADMIN"))):
    room_id = room_id.strip()
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.status = RoomStatus.INACTIVE
    db.commit()
    db.refresh(room)

    return RoomStatusUpdateResponse(
        room_id=str(room.id),
        status=room.status.value if hasattr(room.status, "value") else room.status,
        message="Room marked as inactive"
    )

@router.patch("/admin/rooms/{room_id}/reactivate", response_model=RoomStatusUpdateResponse)
def reactivate_room(room_id: str, db: Session = Depends(get_db), current_user = Depends(require_role("ADMIN"))):
    room_id = room_id.strip()
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.status = RoomStatus.ACTIVE
    room.last_verified_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(room)

    return RoomStatusUpdateResponse(
        room_id=str(room.id),
        status=room.status.value if hasattr(room.status, "value") else room.status,
        message="Room re-verified and reactivated"
    )

@router.post("/admin/submissions/{submission_id}/reject", response_model=RejectionResponse)
def reject_submission(submission_id: str, db: Session = Depends(get_db), current_user = Depends(require_role("ADMIN"))):
    submission_id = submission_id.strip()
    submission = db.query(RoomSubmission).filter(RoomSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.status == "APPROVED":
        raise HTTPException(status_code=409, detail="Cannot reject an already approved submission")

    submission.status = "REJECTED"
    db.commit()
    db.refresh(submission)

    return RejectionResponse(
        submission_id=str(submission.id),
        status=submission.status,
        message="Submission rejected"
    )
