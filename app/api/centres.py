from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.diagnostic_centre import DiagnosticCentre
from app.schemas.diagnostic_centre import DiagnosticCentreCreate, DiagnosticCentreResponse

router = APIRouter()

@router.post("/", response_model=DiagnosticCentreResponse, status_code=status.HTTP_201_CREATED)
def create_centre(centre_in: DiagnosticCentreCreate, db: Session = Depends(get_db)):
    db_centre = DiagnosticCentre(name=centre_in.name, location=centre_in.location)
    db.add(db_centre)
    db.commit()
    db.refresh(db_centre)
    return db_centre

@router.get("/", response_model=List[DiagnosticCentreResponse])
def get_centres(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    centres = db.query(DiagnosticCentre).offset(skip).limit(limit).all()
    return centres

@router.get("/{centre_id}", response_model=DiagnosticCentreResponse)
def get_centre(centre_id: int, db: Session = Depends(get_db)):
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
    if not centre:
        raise HTTPException(status_code=404, detail="Diagnostic centre not found")
    return centre
