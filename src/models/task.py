from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.core.database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    status = Column(String(64), default="pending")
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    project = relationship("Project", backref="tasks")
