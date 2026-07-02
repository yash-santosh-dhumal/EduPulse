import os
import sys

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models import User, UserRole, SchoolClass, Student, Teacher, Subject
from app.admin_models import TeacherClassAssignment
from app.core.security import hash_password

def seed_db():
    session = SessionLocal()
    
    # Check if admin exists
    admin = session.query(User).filter(User.email == "admin@school.com").first()
    if admin:
        print("Database already seeded!")
        return

    print("Seeding database...")
    
    # 1. Create Users
    admin_user = User(
        name="Admin User",
        email="admin@school.com",
        password_hash=hash_password("password123"),
        role=UserRole.ADMIN
    )
    
    teacher_user = User(
        name="John Teacher",
        email="teacher@school.com",
        password_hash=hash_password("password123"),
        role=UserRole.TEACHER
    )
    
    student_user = User(
        name="Alice Student",
        email="student@school.com",
        password_hash=hash_password("password123"),
        role=UserRole.STUDENT
    )
    
    session.add_all([admin_user, teacher_user, student_user])
    session.commit()
    
    # 2. Create School Class
    school_class = SchoolClass(
        name="Grade 10",
        section="A",
        academic_year="2026-2027"
    )
    session.add(school_class)
    session.commit()
    
    # 3. Create Profiles
    teacher_profile = Teacher(
        user_id=teacher_user.id,
        department="Science"
    )
    
    student_profile = Student(
        user_id=student_user.id,
        class_id=school_class.id,
        roll_no="10A-001"
    )
    
    session.add_all([teacher_profile, student_profile])
    session.commit()
    
    # 4. Create Subject and Assignment
    subject = Subject(
        name="Physics",
        code="PHY101"
    )
    session.add(subject)
    session.commit()
    
    tca = TeacherClassAssignment(
        teacher_id=teacher_profile.id,
        class_id=school_class.id,
        subject_id=subject.id
    )
    session.add(tca)
    session.commit()
    
    print("Seeding complete! Credentials:")
    print("Admin:   admin@school.com   / password123")
    print("Teacher: teacher@school.com / password123")
    print("Student: student@school.com / password123")
    
    session.close()

if __name__ == "__main__":
    seed_db()
