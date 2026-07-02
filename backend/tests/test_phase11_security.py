import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

os.environ["JWT_SECRET_KEY"] = "test-secret-key-must-be-at-least-32-characters-long"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_ENV"] = "test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.db.base import Base
from app.api.deps import get_database_session
from app.admin_models import AuditLog
from app.schemas.teacher import AssignmentCreate, NoticeCreate

@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    def override_get_database_session():
        yield db_session

    app.dependency_overrides[get_database_session] = override_get_database_session
    
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_rate_limiting(client: TestClient):
    # Test rate limiting on login endpoint
    # The limit is 5/minute.
    for _ in range(5):
        response = client.post("/api/v1/auth/login", json={"email": "admin@school.com", "password": "wrongpassword"})
        assert response.status_code in [401, 422] # Allowed, but wrong credentials or body
        
    # The 6th request should hit 429 Too Many Requests
    response = client.post("/api/v1/auth/login", json={"email": "admin@school.com", "password": "wrongpassword"})
    assert response.status_code == 429

def test_secure_headers(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"

def test_xss_protection_assignment():
    dirty_title = "<script>alert('xss')</script> Assignment 1"
    dirty_desc = "<p>Clean this up</p>"
    
    assignment = AssignmentCreate(
        title=dirty_title,
        description=dirty_desc,
        deadline="2026-12-31T23:59:59",
        class_id=1
    )
    
    # Bleach strips tags, but leaves inner text by default. 
    # "<script>alert('xss')</script> Assignment 1" becomes "alert('xss') Assignment 1"
    assert "<script>" not in assignment.title
    assert assignment.title == "alert('xss') Assignment 1"
    assert assignment.description == "Clean this up"

def test_xss_protection_notice():
    dirty_title = "<b>Bold Notice</b>"
    dirty_content = "<div>Click <a href='bad'>here</a></div>"
    
    notice = NoticeCreate(
        title=dirty_title,
        body=dirty_content
    )
    
    assert notice.title == "Bold Notice"
    assert notice.body == "Click here"

def test_audit_log_model(db_session: Session):
    log = AuditLog(
        user_id=1,
        action="TEST_ACTION",
        endpoint="/test",
        ip_address="127.0.0.1",
        details="Tested audit logging"
    )
    db_session.add(log)
    db_session.commit()
    
    saved_log = db_session.query(AuditLog).filter_by(action="TEST_ACTION").first()
    assert saved_log is not None
    assert saved_log.ip_address == "127.0.0.1"
    assert saved_log.user_id == 1
