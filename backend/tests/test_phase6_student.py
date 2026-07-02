"""Comprehensive Phase 6 Student Module Tests.

Tests cover:
- Authentication & Authorization (RBAC)
- Data isolation (students can only see their own data)
- All CRUD endpoints
- Input validation
- Edge cases and error handling
- Security: IDOR, role escalation, data leaks
"""
from __future__ import annotations

import json
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

os.environ["JWT_SECRET_KEY"] = "test-secret-key-must-be-at-least-32-characters-long"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_ENV"] = "test"

from datetime import date, datetime, time, timedelta, timezone

from app.core.config import get_settings

get_settings.cache_clear()

from sqlalchemy import create_engine, event, StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import create_access_token
from app.db.base import Base
from app.models import (
    Assignment,
    Attendance,
    AttendanceStatus,
    Examination,
    Mark,
    Notice,
    SchoolClass,
    Student,
    Subject,
    Submission,
    Teacher,
    TimetableEntry,
    User,
    UserRole,
)

# -- Shared in-memory SQLite for testing --
# Using StaticPool so all connections share the same in-memory database
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

Base.metadata.create_all(bind=engine)


def get_test_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


# -- Patch the app: override BOTH get_database_session AND get_db --
from app.api.deps import get_database_session  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

app.dependency_overrides[get_database_session] = get_test_db
app.dependency_overrides[get_db] = get_test_db

from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(app)


# -- Helpers --
def _auth_header(user_id: int) -> dict[str, str]:
    token = create_access_token(str(user_id))
    return {"Authorization": f"Bearer {token}"}


def _seed():
    """Create two students in different classes, a teacher, and an admin."""
    session = TestSession()

    school_class = SchoolClass(name="10", section="A", academic_year="2026")
    school_class_b = SchoolClass(name="11", section="B", academic_year="2026")
    subject = Subject(code="MATH101", name="Mathematics")

    admin_user = User(name="Admin", email="admin@test.com", password_hash="x" * 64, role=UserRole.ADMIN)
    teacher_user = User(name="Teacher", email="teacher@test.com", password_hash="x" * 64, role=UserRole.TEACHER)
    student_user_1 = User(name="Student One", email="s1@test.com", password_hash="x" * 64, role=UserRole.STUDENT)
    student_user_2 = User(name="Student Two", email="s2@test.com", password_hash="x" * 64, role=UserRole.STUDENT)

    session.add_all([school_class, school_class_b, subject, admin_user, teacher_user, student_user_1, student_user_2])
    session.flush()

    teacher = Teacher(user_id=teacher_user.id, department="Math", qualification="MSc", experience=5)
    student_1 = Student(user_id=student_user_1.id, roll_no="10A-001", class_id=school_class.id, section="A", phone="1111", address="Addr1")
    student_2 = Student(user_id=student_user_2.id, roll_no="11B-002", class_id=school_class_b.id, section="B", phone="2222", address="Addr2")

    session.add_all([teacher, student_1, student_2])
    session.flush()

    att1 = Attendance(student_id=student_1.id, date=date.today(), status=AttendanceStatus.PRESENT, teacher_id=teacher.id)
    att2 = Attendance(student_id=student_1.id, date=date.today() - timedelta(days=1), status=AttendanceStatus.ABSENT, teacher_id=teacher.id)
    att_s2 = Attendance(student_id=student_2.id, date=date.today(), status=AttendanceStatus.LATE, teacher_id=teacher.id)

    asgn_1 = Assignment(title="Homework A", description="For class 10A", deadline=datetime.now(timezone.utc) + timedelta(days=7), teacher_id=teacher.id, class_id=school_class.id)
    asgn_2 = Assignment(title="Homework B", description="For class 11B", deadline=datetime.now(timezone.utc) + timedelta(days=7), teacher_id=teacher.id, class_id=school_class_b.id)

    exam = Examination(subject_id=subject.id, class_id=school_class.id, teacher_id=teacher.id, exam_date=date(2026, 7, 15), title="Mid Term")
    session.add_all([att1, att2, att_s2, asgn_1, asgn_2, exam])
    session.flush()

    mark = Mark(exam_id=exam.id, student_id=student_1.id, marks=95.0, grade="A+")
    notice = Notice(author_id=teacher.id, title="Welcome", body="Hello students!", published_at=datetime.now(timezone.utc))

    timetable = TimetableEntry(
        class_id=school_class.id, subject_id=subject.id, teacher_id=teacher.id,
        day_of_week=0, start_time=time(9, 0), end_time=time(9, 45), room="R1", notes="Math"
    )

    session.add_all([mark, notice, timetable])
    session.commit()

    result = {
        "admin_id": admin_user.id,
        "teacher_id": teacher_user.id,
        "student_1_id": student_user_1.id,
        "student_2_id": student_user_2.id,
        "asgn_1_id": asgn_1.id,
        "asgn_2_id": asgn_2.id,
    }
    session.close()
    return result


data = _seed()

passed = 0
failed = 0
errors = []


def test(name):
    def decorator(fn):
        global passed, failed
        try:
            fn()
            passed += 1
            print(f"  PASS  {name}")
        except Exception as e:
            failed += 1
            errors.append((name, str(e)))
            print(f"  FAIL  {name}: {e}")
    return decorator


print()
print("=" * 60)
print("  PHASE 6 STUDENT MODULE - SECURITY & FUNCTIONAL TESTS")
print("=" * 60)

# ========================================
# 1. AUTHENTICATION TESTS
# ========================================

print()
print("-- Authentication --")

@test("Unauthenticated request returns 401 or 403")
def _():
    for ep in ["/api/v1/student/dashboard", "/api/v1/student/profile",
               "/api/v1/student/attendance", "/api/v1/student/assignments",
               "/api/v1/student/marks", "/api/v1/student/notices",
               "/api/v1/student/timetable"]:
        r = client.get(ep)
        assert r.status_code in (401, 403), f"{ep} returned {r.status_code}"

@test("Invalid JWT returns 401")
def _():
    r = client.get("/api/v1/student/dashboard", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert r.status_code == 401

# ========================================
# 2. AUTHORIZATION / RBAC TESTS
# ========================================

print()
print("-- Authorization (RBAC) --")

@test("Admin cannot access student endpoints")
def _():
    h = _auth_header(data["admin_id"])
    r = client.get("/api/v1/student/dashboard", headers=h)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"

@test("Teacher cannot access student endpoints")
def _():
    h = _auth_header(data["teacher_id"])
    r = client.get("/api/v1/student/dashboard", headers=h)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"

# ========================================
# 3. DASHBOARD TESTS
# ========================================

print()
print("-- Student Dashboard --")

@test("Student 1 dashboard returns correct profile")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.get("/api/v1/student/dashboard", headers=h)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert body["profile"]["name"] == "Student One"
    assert body["profile"]["email"] == "s1@test.com"
    assert body["profile"]["roll_no"] == "10A-001"

@test("Dashboard contains attendance summary")
def _():
    h = _auth_header(data["student_1_id"])
    body = client.get("/api/v1/student/dashboard", headers=h).json()
    summary = body["attendance_summary"]
    assert summary["total_days"] == 2
    assert summary["present_days"] == 1
    assert summary["absent_days"] == 1
    assert summary["attendance_percentage"] == 50.0

@test("Dashboard only shows assignments for student's class")
def _():
    h = _auth_header(data["student_1_id"])
    body = client.get("/api/v1/student/dashboard", headers=h).json()
    titles = [a["title"] for a in body["upcoming_assignments"]]
    assert "Homework A" in titles
    assert "Homework B" not in titles, "SECURITY: Student sees assignments from another class!"

@test("Dashboard shows marks, notices, timetable")
def _():
    h = _auth_header(data["student_1_id"])
    body = client.get("/api/v1/student/dashboard", headers=h).json()
    assert len(body["recent_marks"]) >= 1
    assert len(body["notices"]) >= 1
    assert len(body["timetable"]) >= 1

# ========================================
# 4. DATA ISOLATION TESTS (IDOR prevention)
# ========================================

print()
print("-- Data Isolation (IDOR) --")

@test("Student 2 cannot see Student 1's attendance")
def _():
    h = _auth_header(data["student_2_id"])
    body = client.get("/api/v1/student/attendance", headers=h).json()
    for row in body:
        assert row["status"] != "present", "SECURITY: Student 2 sees Student 1's PRESENT attendance!"

@test("Student 2 cannot see Student 1's assignments (class isolation)")
def _():
    h = _auth_header(data["student_2_id"])
    body = client.get("/api/v1/student/assignments", headers=h).json()
    titles = [a["title"] for a in body]
    assert "Homework A" not in titles, "SECURITY: Student 2 sees class 10A assignments!"
    assert "Homework B" in titles

@test("Student 2 cannot see Student 1's marks")
def _():
    h = _auth_header(data["student_2_id"])
    body = client.get("/api/v1/student/marks", headers=h).json()
    assert len(body) == 0, "SECURITY: Student 2 sees Student 1's marks!"

@test("Student 2 sees only their own timetable (class isolation)")
def _():
    h = _auth_header(data["student_2_id"])
    body = client.get("/api/v1/student/timetable", headers=h).json()
    assert len(body) == 0, "SECURITY: Student 2 sees class 10A timetable!"

# ========================================
# 5. PROFILE TESTS
# ========================================

print()
print("-- Profile --")

@test("Student can view own profile")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.get("/api/v1/student/profile", headers=h)
    assert r.status_code == 200
    assert r.json()["email"] == "s1@test.com"

@test("Student can update phone and address")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.patch("/api/v1/student/profile", headers=h, json={"phone": "9876543210", "address": "New Addr"})
    assert r.status_code == 200
    assert r.json()["phone"] == "9876543210"
    assert r.json()["address"] == "New Addr"

@test("Profile update rejects duplicate email")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.patch("/api/v1/student/profile", headers=h, json={"email": "s2@test.com"})
    assert r.status_code == 409, f"Expected 409 for duplicate email, got {r.status_code}"

@test("Profile update validates name min length")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.patch("/api/v1/student/profile", headers=h, json={"name": "A"})
    assert r.status_code == 422, f"Expected 422 for short name, got {r.status_code}"

@test("Profile does not leak password_hash")
def _():
    h = _auth_header(data["student_1_id"])
    body = client.get("/api/v1/student/profile", headers=h).json()
    body_str = json.dumps(body).lower()
    assert "password_hash" not in body_str, "SECURITY: password_hash exposed in profile response!"
    assert "password" not in body_str, "SECURITY: password exposed in profile response!"

# ========================================
# 6. ASSIGNMENT SUBMISSION TESTS
# ========================================

print()
print("-- Assignment Submission --")

@test("Student can submit assignment for their class")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.post(f"/api/v1/student/assignments/{data['asgn_1_id']}/submit",
                    headers=h, json={"file_url": "https://example.com/my-work.pdf"})
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"

@test("Duplicate submission returns 409")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.post(f"/api/v1/student/assignments/{data['asgn_1_id']}/submit",
                    headers=h, json={"file_url": "https://example.com/dup.pdf"})
    assert r.status_code == 409, f"Expected 409, got {r.status_code}"

@test("Student cannot submit to assignment of another class")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.post(f"/api/v1/student/assignments/{data['asgn_2_id']}/submit",
                    headers=h, json={"file_url": "https://example.com/x.pdf"})
    assert r.status_code == 403, f"SECURITY: Student submitted to wrong class assignment! Got {r.status_code}"

@test("Submit to non-existent assignment returns 404")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.post("/api/v1/student/assignments/99999/submit",
                    headers=h, json={"file_url": "https://example.com/x.pdf"})
    assert r.status_code == 404

@test("Empty file_url rejected by validation")
def _():
    h = _auth_header(data["student_1_id"])
    r = client.post(f"/api/v1/student/assignments/{data['asgn_1_id']}/submit",
                    headers=h, json={"file_url": ""})
    assert r.status_code == 422, f"Expected 422 for empty file_url, got {r.status_code}"

# ========================================
# 7. NOTICES
# ========================================

print()
print("-- Notices --")

@test("Both students see the same notices")
def _():
    h1 = _auth_header(data["student_1_id"])
    h2 = _auth_header(data["student_2_id"])
    r1 = client.get("/api/v1/student/notices", headers=h1)
    r2 = client.get("/api/v1/student/notices", headers=h2)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert len(r1.json()) == len(r2.json())

# ========================================
# 8. RESPONSE SCHEMA SECURITY
# ========================================

print()
print("-- Response Schema Security --")

SENSITIVE_FIELDS = {"password_hash", "jwt_secret", "secret_key"}

@test("Dashboard response has no sensitive fields")
def _():
    h = _auth_header(data["student_1_id"])
    body_str = json.dumps(client.get("/api/v1/student/dashboard", headers=h).json()).lower()
    for field in SENSITIVE_FIELDS:
        assert field not in body_str, f"SECURITY: '{field}' found in dashboard response!"

@test("Attendance response has no sensitive fields")
def _():
    h = _auth_header(data["student_1_id"])
    body_str = json.dumps(client.get("/api/v1/student/attendance", headers=h).json()).lower()
    for field in SENSITIVE_FIELDS:
        assert field not in body_str, f"SECURITY: '{field}' found in attendance response!"

@test("Marks response has no sensitive fields")
def _():
    h = _auth_header(data["student_1_id"])
    body_str = json.dumps(client.get("/api/v1/student/marks", headers=h).json()).lower()
    for field in SENSITIVE_FIELDS:
        assert field not in body_str, f"SECURITY: '{field}' found in marks response!"


# ========================================
# RESULTS
# ========================================

print()
print("=" * 60)
print(f"  RESULTS:  {passed} passed,  {failed} failed")
print("=" * 60)

if errors:
    print()
    print("  FAILURES:")
    for name, msg in errors:
        print(f"    X {name}")
        print(f"      {msg}")
        print()

sys.exit(1 if failed else 0)
