from pydantic import BaseModel
from datetime import datetime
from typing import List

class DiagnosticCentreBase(BaseModel):
    name: str
    location: str

class DiagnosticCentreCreate(DiagnosticCentreBase):
    pass

class DiagnosticCentreResponse(DiagnosticCentreBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
