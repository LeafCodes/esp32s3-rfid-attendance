from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Card
from app.schemas import CardCreate, CardResponse

router = APIRouter(prefix="/api/cards", tags=["cards"])

# In-memory enrollment state (mutated in-place to preserve reference across imports)
enrollment_state = {
    "active": False,
    "name": "",
    "uid": None,
    "message": ""
}


@router.get("/", response_model=List[CardResponse])
async def list_cards(db: Session = Depends(get_db)):
    return db.query(Card).filter(Card.active == True).all()


@router.post("/", response_model=CardResponse)
async def add_card(card: CardCreate, db: Session = Depends(get_db)):
    existing = db.query(Card).filter(Card.uid == card.uid.upper()).first()
    if existing:
        if existing.active:
            raise HTTPException(status_code=400, detail="Card UID already exists")
        existing.active = True
        existing.name = card.name
        db.commit()
        db.refresh(existing)
        return existing

    new_card = Card(uid=card.uid.upper(), name=card.name)
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


@router.delete("/{card_id}")
async def delete_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.active = False
    db.commit()
    return {"status": "ok", "message": "Card deleted"}


@router.get("/sync")
async def sync_cards(db: Session = Depends(get_db)):
    cards = db.query(Card).filter(Card.active == True).all()
    return [{"uid": c.uid, "name": c.name} for c in cards]


@router.post("/enroll/start")
async def start_enrollment(data: dict):
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nama tidak boleh kosong")
    
    enrollment_state["active"] = True
    enrollment_state["name"] = name
    enrollment_state["uid"] = None
    enrollment_state["message"] = f"Silakan tempelkan kartu RFID baru untuk: {name}"
    print(f"[ENROLL START] Active for: {name}")
    return enrollment_state


@router.get("/enroll/status")
async def get_enrollment_status():
    return enrollment_state


@router.post("/enroll/cancel")
async def cancel_enrollment():
    enrollment_state["active"] = False
    enrollment_state["name"] = ""
    enrollment_state["uid"] = None
    enrollment_state["message"] = ""
    return enrollment_state
