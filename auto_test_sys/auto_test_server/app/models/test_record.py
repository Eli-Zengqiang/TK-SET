from sqlalchemy import Column, String, Text, Boolean
from app.models.base import BaseModel

class TestRecord(BaseModel):
    """测试记录模型"""
    __tablename__ = "test_records"
    
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(20), default="pending")
    result = Column(Text)
    is_passed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<TestRecord(id={self.id}, name='{self.name}', status='{self.status}')>"