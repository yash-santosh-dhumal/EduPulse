from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db.base import Base
from .models import SchoolClass, Subject, Teacher, TimestampMixin


class TeacherClassAssignment(Base, TimestampMixin):
    __tablename__ = "teacher_class_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("school_classes.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[int | None] = mapped_column(ForeignKey("subjects.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(Text)

    teacher: Mapped[Teacher] = relationship()
    school_class: Mapped[SchoolClass] = relationship()
    subject: Mapped[Subject | None] = relationship()

    __table_args__ = (UniqueConstraint("teacher_id", "class_id", "subject_id", name="uq_teacher_class_subject"),)


class SchoolSetting(Base, TimestampMixin):
    __tablename__ = "school_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
