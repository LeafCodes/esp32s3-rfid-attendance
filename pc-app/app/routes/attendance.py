from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models import Attendance, Card
from app.schemas import AttendanceCreate, AttendanceResponse
from app.routes import cards

router = APIRouter(prefix="/api", tags=["attendance"])

WIB = timezone(timedelta(hours=7))

def get_now_wib():
    return datetime.now(WIB).replace(tzinfo=None)


@router.post("/attendance")
async def record_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    card_uid = data.uid.upper()
    card = db.query(Card).filter(Card.uid == card_uid, Card.active == True).first()
    is_newly_enrolled = False

    print(f"[ATTENDANCE SCAN] UID={card_uid}, CardFound={card is not None}, EnrollActive={cards.enrollment_state.get('active')}")

    # Handle Enrollment Mode if card is not registered yet
    if not card and cards.enrollment_state.get("active"):
        name = cards.enrollment_state.get("name", "Pengguna Baru")
        existing_any = db.query(Card).filter(Card.uid == card_uid).first()
        if existing_any:
            existing_any.active = True
            existing_any.name = name
            card = existing_any
        else:
            card = Card(uid=card_uid, name=name)
            db.add(card)
        db.commit()
        db.refresh(card)

        cards.enrollment_state["active"] = False
        cards.enrollment_state["uid"] = card_uid
        cards.enrollment_state["message"] = f"Berhasil mendaftarkan {name} ({card_uid})!"
        print(f"[ENROLL ONLY] Registered {name} with UID {card_uid} (No attendance log created)")

        return {
            "status": "ok",
            "message": f"Kartu {name} berhasil terdaftar!",
            "uid": card_uid,
            "name": name,
            "inout": "TERDAFTAR"
        }

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    last_attendance = (
        db.query(Attendance)
        .filter(Attendance.uid == card.uid)
        .order_by(desc(Attendance.timestamp))
        .first()
    )

    now_wib = get_now_wib()

    if data.timestamp:
        try:
            ts = datetime.fromisoformat(data.timestamp)
        except Exception:
            ts = now_wib
    else:
        ts = now_wib

    # Anti Double-Tap Protection (10s cooldown)
    if last_attendance:
        time_diff = abs((ts - last_attendance.timestamp).total_seconds())
        if time_diff < 10:
            return {
                "status": "ok",
                "message": f"Cooldown active. Retained {last_attendance.status} for {card.name}",
                "uid": card.uid,
                "name": card.name,
                "inout": last_attendance.status
            }

    new_status = "OUT" if (last_attendance and last_attendance.status == "IN") else "IN"

    record = Attendance(
        card_id=card.id,
        uid=card.uid,
        name=card.name,
        timestamp=ts,
        status=new_status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"status": "ok", "message": f"{new_status} recorded for {card.name}", "uid": card.uid, "name": card.name, "inout": new_status}


@router.get("/attendance")
async def get_attendance(
    limit: int = Query(50, ge=1, le=1000),
    start: Optional[str] = None,
    end: Optional[str] = None,
    uid: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Attendance)

    if uid:
        query = query.filter(Attendance.uid == uid)
    if status:
        query = query.filter(Attendance.status == status)
    if start:
        try:
            start_dt = datetime.fromisoformat(start)
            query = query.filter(Attendance.timestamp >= start_dt)
        except:
            pass
    if end:
        try:
            end_dt = datetime.fromisoformat(end)
            query = query.filter(Attendance.timestamp <= end_dt)
        except:
            pass

    total = query.count()
    records = query.order_by(desc(Attendance.timestamp)).limit(limit).all()

    return {"attendances": records, "total": total}


@router.get("/health")
async def health():
    return {"status": "ok"}
