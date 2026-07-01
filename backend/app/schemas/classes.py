from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SchoolClassBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    section: str = Field(min_length=1, max_length=20)
    academic_year: str = Field(min_length=4, max_length=20)


class SchoolClassCreate(SchoolClassBase):
    pass


class SchoolClassUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    section: str | None = Field(default=None, min_length=1, max_length=20)
    academic_year: str | None = Field(default=None, min_length=4, max_length=20)


class SchoolClassRead(SchoolClassBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeacherAssignmentCreate(BaseModel):
    teacher_id: int
    subject_id: int | None = None
    notes: str | None = None


class TeacherAssignmentRead(BaseModel):
    id: int
    teacher_id: int
    class_id: int
    subject_id: int | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentAssignmentRequest(BaseModel):
    student_id: int


class StudentAssignmentRead(BaseModel):
    student_id: int
    class_id: int | None
    class_name: str | None = None
    section: str | None = None
    roll_no: str | None = None

