import json
import uuid
from typing import List
from app.schemas.room_schema import RoomSubmissionOut
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.room_schema import RoomSubmissionCreate, RoomSubmissionResponse
from app.models.models import RoomSubmission

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
def get_all_submissions(db: Session = Depends(get_db)):
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