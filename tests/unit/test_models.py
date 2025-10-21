"""Unit tests for database models (sqlite in-memory)"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.models.base import Base
from src.models.user import User
from src.models.project import Project
from src.models.transcription import Transcription

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    try:
        yield s
    finally:
        s.close()

def test_user_creation(db_session):
    u = User(email="t@e.com", username="tuser", hashed_password="x")
    db_session.add(u); db_session.commit()
    assert u.id is not None and u.is_active is True

def test_project_relationships(db_session):
    u = User(email="p@e.com", username="puser", hashed_password="x")
    db_session.add(u); db_session.commit()
    p = Project(name="P1", owner_id=u.id)
    db_session.add(p); db_session.commit()
    t = Transcription(file_path="a.mp3", text="hi", project_id=p.id)
    db_session.add(t); db_session.commit()
    assert len(p.transcriptions) == 1
