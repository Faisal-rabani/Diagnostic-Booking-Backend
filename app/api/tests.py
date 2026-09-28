from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.diagnostic_test import DiagnosticTest
from app.models.diagnostic_centre import DiagnosticCentre
from app.schemas.diagnostic_test import DiagnosticTestCreate, DiagnosticTestResponse

router = APIRouter()

@router.post("/", response_model=DiagnosticTestResponse, status_code=status.HTTP_201_CREATED)
def create_test(test_in: DiagnosticTestCreate, db: Session = Depends(get_db)):
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == test_in.centre_id).first()
    if not centre:
        raise HTTPException(status_code=400, detail="Invalid centre ID")
    
    db_test = DiagnosticTest(
        name=test_in.name,
        description=test_in.description,
        price=test_in.price,
        centre_id=test_in.centre_id
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@router.get("/", response_model=List[DiagnosticTestResponse])
def get_tests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tests = db.query(DiagnosticTest).offset(skip).limit(limit).all()
    return tests

@router.get("/{test_id}", response_model=DiagnosticTestResponse)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Diagnostic test not found")
    return test
