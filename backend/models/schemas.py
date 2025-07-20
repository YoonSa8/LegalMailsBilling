from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime

class EmailBase(BaseModel):
    subject: Optional[str] = None
    to: Optional[str] = None
    from_: Optional[str] = None
    body: str

class EmailSummary(BaseModel):
    summary: str
    type: Literal["TimeEntry", "ExpenseEntry"]
    duration: Optional[float] = None
    rate: Optional[float] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    expense_type: Optional[str] = None
    matter_id: int 

class EmailWithSummary(EmailBase):
    summary: EmailSummary

class ClioActivityResponse(BaseModel):
    status: str
    activities_created: List[dict]
    errors: Optional[List[str]] = None

class TokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None