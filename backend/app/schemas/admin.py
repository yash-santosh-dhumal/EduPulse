from pydantic import BaseModel


class AdminDashboardRead(BaseModel):
    total_users: int
    total_teachers: int
    total_students: int
    total_classes: int
    total_teacher_assignments: int
    total_settings: int
    total_assignments: int
    total_examinations: int
    total_notices: int

