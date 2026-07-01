from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..admin_models import SchoolSetting, TeacherClassAssignment
from ..models import Assignment, Examination, Notice, SchoolClass, Student, Subject, Teacher, User


def list_school_classes(session: Session) -> list[SchoolClass]:
    return list(session.scalars(select(SchoolClass).order_by(SchoolClass.id)).all())


def create_school_class(session: Session, *, name: str, section: str, academic_year: str) -> SchoolClass:
    existing = session.scalar(
        select(SchoolClass).where(
            SchoolClass.name == name,
            SchoolClass.section == section,
            SchoolClass.academic_year == academic_year,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Class already exists")

    school_class = SchoolClass(name=name, section=section, academic_year=academic_year)
    session.add(school_class)
    session.flush()
    return school_class


def update_school_class(
    session: Session,
    class_id: int,
    *,
    name: str | None = None,
    section: str | None = None,
    academic_year: str | None = None,
) -> SchoolClass:
    school_class = session.get(SchoolClass, class_id)
    if school_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    next_name = name if name is not None else school_class.name
    next_section = section if section is not None else school_class.section
    next_academic_year = academic_year if academic_year is not None else school_class.academic_year

    duplicate = session.scalar(
        select(SchoolClass).where(
            SchoolClass.id != class_id,
            SchoolClass.name == next_name,
            SchoolClass.section == next_section,
            SchoolClass.academic_year == next_academic_year,
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Class already exists")

    school_class.name = next_name
    school_class.section = next_section
    school_class.academic_year = next_academic_year
    return school_class


def delete_school_class(session: Session, class_id: int) -> None:
    school_class = session.get(SchoolClass, class_id)
    if school_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
    session.delete(school_class)


def assign_teacher_to_class(
    session: Session,
    class_id: int,
    *,
    teacher_id: int,
    subject_id: int | None = None,
    notes: str | None = None,
) -> TeacherClassAssignment:
    school_class = session.get(SchoolClass, class_id)
    if school_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    teacher = session.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    subject = None
    if subject_id is not None:
        subject = session.get(Subject, subject_id)
        if subject is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    duplicate_query = select(TeacherClassAssignment).where(
        TeacherClassAssignment.teacher_id == teacher_id,
        TeacherClassAssignment.class_id == class_id,
    )
    duplicate_query = (
        duplicate_query.where(TeacherClassAssignment.subject_id.is_(None))
        if subject_id is None
        else duplicate_query.where(TeacherClassAssignment.subject_id == subject_id)
    )
    existing = session.scalar(duplicate_query)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Teacher already assigned to class")

    assignment = TeacherClassAssignment(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject.id if subject is not None else None,
        notes=notes,
    )
    session.add(assignment)
    session.flush()
    return assignment


def assign_student_to_class(session: Session, class_id: int, student_id: int) -> Student:
    school_class = session.get(SchoolClass, class_id)
    if school_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    student = session.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    student.school_class = school_class
    student.section = school_class.section
    return student


def list_school_settings(session: Session) -> list[SchoolSetting]:
    return list(session.scalars(select(SchoolSetting).order_by(SchoolSetting.key)).all())


def upsert_school_setting(session: Session, key: str, value: str, description: str | None = None) -> SchoolSetting:
    setting = session.scalar(select(SchoolSetting).where(SchoolSetting.key == key))
    if setting is None:
        setting = SchoolSetting(key=key, value=value, description=description)
        session.add(setting)
    else:
        setting.value = value
        setting.description = description
    session.flush()
    return setting


def get_admin_dashboard_summary(session: Session) -> dict[str, int]:
    return {
        "total_users": session.scalar(select(func.count()).select_from(User)) or 0,
        "total_teachers": session.scalar(select(func.count()).select_from(Teacher)) or 0,
        "total_students": session.scalar(select(func.count()).select_from(Student)) or 0,
        "total_classes": session.scalar(select(func.count()).select_from(SchoolClass)) or 0,
        "total_teacher_assignments": session.scalar(select(func.count()).select_from(TeacherClassAssignment)) or 0,
        "total_settings": session.scalar(select(func.count()).select_from(SchoolSetting)) or 0,
        "total_assignments": session.scalar(select(func.count()).select_from(Assignment)) or 0,
        "total_examinations": session.scalar(select(func.count()).select_from(Examination)) or 0,
        "total_notices": session.scalar(select(func.count()).select_from(Notice)) or 0,
    }
