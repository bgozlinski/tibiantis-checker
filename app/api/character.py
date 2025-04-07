from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.character import CharacterCreate, CharacterOut, CharacterUpdate
from app.db.models.character import Character
from app.db.session import SessionLocal

from app.utils.player_scraper import player_scrape

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[CharacterOut])
def get_characters(db: Session = Depends(get_db)):
    return db.query(Character).all()


@router.get("/{character_id}", response_model=CharacterOut)
def get_character(character_id: int, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char


@router.post("/", response_model=CharacterOut)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    db_char = Character(**character.model_dump())
    db.add(db_char)
    db.commit()
    db.refresh(db_char)
    return db_char


@router.delete("/{character_id}")
def delete_character(character_id: int, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(char)
    db.commit()
    return {"detail": "Character deleted"}


@router.patch("/{character_id}", response_model=CharacterOut)
def update_character(character_id: int, updates: CharacterUpdate, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(char, key, value)

    db.commit()
    db.refresh(char)
    return char


@router.patch("/{character_id}/update_last_login", response_model=CharacterOut)
def update_last_login(character_id: int, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    try:
        scraped_data = player_scrape(char.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    from datetime import datetime
    try:
        parsed_login = scraped_data["last_login"]
        parsed_login = parsed_login.replace("CEST", "").replace("CET", "").strip()
        dt = datetime.strptime(parsed_login, "%d %b %Y %H:%M:%S")
        char.last_login = dt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not parse last_login: {e}")

    db.commit()
    db.refresh(char)
    return char