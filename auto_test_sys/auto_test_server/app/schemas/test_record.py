from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TestRecordBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "pending"

class TestRecordCreate(TestRecordBase):
    pass

class TestRecordUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    result: Optional[str] = None
    is_passed: Optional[bool] = None

class TestRecordInDB(TestRecordBase):
    id: int
    result: Optional[str] = None
    is_passed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True