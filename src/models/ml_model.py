from sqlalchemy import Column, Integer, String, DateTime, func
from src.core.database import Base

class MLModel(Base):
    __tablename__ = "ml_models"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(64), nullable=False)
    path = Column(String(1024), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
