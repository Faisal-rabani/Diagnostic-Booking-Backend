from pydantic import BaseModel
from datetime import datetime

class DiagnosticTestBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    centre_id: int

class DiagnosticTestCreate(DiagnosticTestBase):
    pass

class DiagnosticTestResponse(DiagnosticTestBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
