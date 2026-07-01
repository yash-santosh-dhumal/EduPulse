from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from ...api.deps import get_database_session, require_roles
from ...models import UserRole
from ...schemas.admin import AdminDashboardRead
from ...schemas.classes import (
    SchoolClassCreate,
    SchoolClassRead,
    SchoolClassUpdate,
    StudentAssignmentRead,
    StudentAssignmentRequest,
    TeacherAssignmentCreate,
    TeacherAssignmentRead,
)
from ...schemas.settings import SchoolSettingRead, SchoolSettingUpsert
from ...services.admin_service import (
    assign_student_to_class,
    assign_teacher_to_class,
    create_school_class,
    delete_school_class,
    get_admin_dashboard_summary,
    list_school_classes,
    list_school_settings,
    upsert_school_setting,
    update_school_class,
)


router = APIRouter(prefix="/admin", tags=["admin"])
admin_guard = Depends(require_roles(UserRole.ADMIN))


@router.get("/dashboard", response_model=AdminDashboardRead, dependencies=[admin_guard])
def dashboard(session: Session = Depends(get_database_session)) -> dict[str, int]:
    return get_admin_dashboard_summary(session)


@router.get("/classes", response_model=list[SchoolClassRead], dependencies=[admin_guard])
def get_classes(session: Session = Depends(get_database_session)) -> list:
    return list_school_classes(session)


@router.post("/classes", response_model=SchoolClassRead, status_code=status.HTTP_201_CREATED, dependencies=[admin_guard])
def create_class(payload: SchoolClassCreate, session: Session = Depends(get_database_session)) -> object:
    school_class = create_school_class(
        session,
        name=payload.name,
        section=payload.section,
        academic_year=payload.academic_year,
    )
    session.commit()
    return school_class


@router.put("/classes/{class_id}", response_model=SchoolClassRead, dependencies=[admin_guard])
def edit_class(class_id: int, payload: SchoolClassUpdate, session: Session = Depends(get_database_session)) -> object:
    school_class = update_school_class(
        session,
        class_id,
        name=payload.name,
        section=payload.section,
        academic_year=payload.academic_year,
    )
    session.commit()
    return school_class


@router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_guard])
def remove_class(class_id: int, session: Session = Depends(get_database_session)) -> Response:
    delete_school_class(session, class_id)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/classes/{class_id}/assign-teacher", response_model=TeacherAssignmentRead, dependencies=[admin_guard])
def assign_teacher(class_id: int, payload: TeacherAssignmentCreate, session: Session = Depends(get_database_session)) -> object:
    assignment = assign_teacher_to_class(
        session,
        class_id,
        teacher_id=payload.teacher_id,
        subject_id=payload.subject_id,
        notes=payload.notes,
    )
    session.commit()
    return assignment


@router.post("/classes/{class_id}/assign-student", response_model=StudentAssignmentRead, dependencies=[admin_guard])
def assign_student(class_id: int, payload: StudentAssignmentRequest, session: Session = Depends(get_database_session)) -> StudentAssignmentRead:
    student = assign_student_to_class(session, class_id, payload.student_id)
    session.commit()
    return StudentAssignmentRead(
        student_id=student.id,
        class_id=student.class_id,
        class_name=student.school_class.name if student.school_class else None,
        section=student.section,
        roll_no=student.roll_no,
    )


@router.get("/settings", response_model=list[SchoolSettingRead], dependencies=[admin_guard])
def get_settings(session: Session = Depends(get_database_session)) -> list:
    return list_school_settings(session)


@router.put("/settings/{key}", response_model=SchoolSettingRead, dependencies=[admin_guard])
def update_setting(key: str, payload: SchoolSettingUpsert, session: Session = Depends(get_database_session)) -> object:
    setting = upsert_school_setting(session, key, payload.value, payload.description)
    session.commit()
    return setting