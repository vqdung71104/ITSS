"""
from fastapi import APIRouter, Depends, HTTPException, status
from models.report_model import Report
from models.task_model import Task
from models.user_model import User
from schemas.report_schemas import ReportCreate, ReportResponse
from routes.user_routes import get_current_user
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ReportResponse)
async def create_report(report: ReportCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    task = await Task.get(report.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    assigned_students = await task.fetch_link("assigned_students") or []
    logger.info(f"Current user ID: {current_user.id}, Assigned students IDs: {[str(student.id) for student in assigned_students]}")
    if str(current_user.id) not in [str(student.id) for student in assigned_students]:
        raise HTTPException(status_code=403, detail="Not authorized to report on this task")

    new_report = Report(
        content=report.content,
        student=current_user,
        task=task
    )
    await new_report.insert()
    logger.info(f"Created new report: {new_report.id}")
    return ReportResponse(
        id=new_report.id,  
        content=new_report.content,
        student={"id": str(new_report.student.id), "ho_ten": new_report.student.ho_ten},
        task={"id": str(new_report.task.id), "title": new_report.task.title},
        created_at=new_report.created_at
    )

@router.get("/", response_model=list[ReportResponse])
async def get_reports(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    reports = await Report.find({"student.$id": current_user.id}).to_list()
    return [
        ReportResponse(
            id=report.id,  # Không cần str() vì PyObjectId xử lý
            content=report.content,
            student={"id": str(report.student.id), "ho_ten": report.student.ho_ten},
            task={"id": str(report.task.id), "title": report.task.title},
            created_at=report.created_at
        )
        for report in reports
    ]

@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(report_id: str, report: ReportCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    db_report = await Report.get(report_id)
    if not db_report or str(db_report.student.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")

    task = await Task.get(report.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    assigned_students = await task.fetch_link("assigned_students") or []
    logger.info(f"Current user ID: {current_user.id}, Assigned students IDs: {[str(student.id) for student in assigned_students]}")
    if str(current_user.id) not in [str(student.id) for student in assigned_students]:
        raise HTTPException(status_code=403, detail="Not authorized to report on this task")

    db_report.content = report.content
    db_report.task = task
    await db_report.save()
    logger.info(f"Updated report: {db_report.id}")
    return ReportResponse(
        id=db_report.id,  # Không cần str() vì PyObjectId xử lý
        content=db_report.content,
        student={"id": str(db_report.student.id), "ho_ten": db_report.student.ho_ten},
        task={"id": str(db_report.task.id), "title": db_report.task.title},
        created_at=db_report.created_at
    )

@router.delete("/{report_id}")
async def delete_report(report_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    report = await Report.get(report_id)
    if not report or str(report.student.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")
    
    await report.delete()
    logger.info(f"Deleted report: {report_id}")
    return {"message": "Report deleted"}
"""
"""
from fastapi import APIRouter, Depends, HTTPException, status
from models.report_model import Report
from models.task_model import Task
from models.user_model import User
from schemas.report_schemas import ReportCreate, ReportResponse
from routes.user_routes import get_current_user
from beanie import Link
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ReportResponse)
async def create_report(report: ReportCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    task = await Task.get(report.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_report = Report(
        content=report.content,
        student=current_user,
        task=task
    )
    await new_report.insert()
    logger.info(f"Created new report: {new_report.id}")
    return ReportResponse(
        id=new_report.id,
        content=new_report.content,
        student={"id": str(new_report.student.id), "ho_ten": new_report.student.ho_ten},
        task={"id": str(new_report.task.id), "title": new_report.task.title},
        created_at=new_report.created_at
    )

@router.get("/", response_model=list[ReportResponse])
async def get_reports(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    reports = await Report.find({"student.$id": current_user.id}).to_list()
    result = []
    for report in reports:
        # Resolve Link[User]
        await report.student.fetch()
        if isinstance(report.student, Link):
            logger.error(f"Failed to resolve student for report {report.id}")
            continue  # Bỏ qua report nếu student không tồn tại

        # Resolve Link[Task]
        await report.task.fetch()
        if isinstance(report.task, Link):
            logger.error(f"Failed to resolve task for report {report.id}")
            continue  # Bỏ qua report nếu task không tồn tại

        result.append(ReportResponse(
            id=report.id,
            content=report.content,
            student={"id": str(report.student.id), "ho_ten": report.student.ho_ten},
            task={"id": str(report.task.id), "title": report.task.title},
            created_at=report.created_at
        ))
    return result

@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(report_id: str, report: ReportCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    db_report = await Report.get(report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Resolve Link[User]
    await db_report.student.fetch()
    if isinstance(db_report.student, Link):
        logger.error(f"Failed to resolve student for report {db_report.id}")
        raise HTTPException(status_code=404, detail="Student associated with report not found")

    if str(db_report.student.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")

    task = await Task.get(report.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_report.content = report.content
    db_report.task = task
    await db_report.save()
    logger.info(f"Updated report: {db_report.id}")
    
    # Resolve Link[Task] trước khi trả về
    await db_report.task.fetch()
    if isinstance(db_report.task, Link):
        logger.error(f"Failed to resolve task for report {db_report.id}")
        raise HTTPException(status_code=404, detail="Task associated with report not found")

    return ReportResponse(
        id=db_report.id,
        content=db_report.content,
        student={"id": str(db_report.student.id), "ho_ten": db_report.student.ho_ten},
        task={"id": str(db_report.task.id), "title": db_report.task.title},
        created_at=db_report.created_at
    )

@router.delete("/{report_id}")
async def delete_report(report_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    report = await Report.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Resolve Link[User]
    await report.student.fetch()
    if isinstance(report.student, Link):
        logger.error(f"Failed to resolve student for report {report.id}")
        raise HTTPException(status_code=404, detail="Student associated with report not found")

    if str(report.student.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")
    
    await report.delete()
    logger.info(f"Deleted report: {report_id}")
    return {"message": "Report deleted"}
"""


from fastapi import APIRouter, Depends, HTTPException, status
from models.report_model import Report
from models.task_model import Task
from models.user_model import User
from schemas.report_schemas import ReportCreate, ReportResponse
from routes.user_routes import get_current_user
from beanie import Link
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ReportResponse)
async def create_report(report: ReportCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    task = await Task.get(report.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Resolve assigned_students
    assigned_students = await task.fetch_link("assigned_students") or []
    if not assigned_students:
        logger.error(f"Task {task.id} has no assigned students")
        raise HTTPException(status_code=403, detail="No students assigned to this task")

    # Kiểm tra current_user có trong assigned_students hay không
    if str(current_user.id) not in [str(student.id) for student in assigned_students]:
        logger.info(f"User {current_user.id} is not authorized to report on task {task.id}")
        raise HTTPException(status_code=403, detail="Not authorized to report on this task")

    new_report = Report(
        content=report.content,
        student=current_user,
        task=task
    )
    await new_report.insert()
    logger.info(f"Created new report: {new_report.id}")
    return ReportResponse(
        id=new_report.id,
        content=new_report.content,
        student={"id": str(new_report.student.id), "ho_ten": new_report.student.ho_ten},
        task={"id": str(new_report.task.id), "title": new_report.task.title},
        created_at=new_report.created_at
    )

@router.get("/", response_model=list[ReportResponse])
async def get_reports(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    reports = await Report.find({"student.$id": current_user.id}).to_list()
    result = []
    for report in reports:
        # Resolve Link[User]
        await report.student.fetch()
        if isinstance(report.student, Link):
            logger.error(f"Failed to resolve student for report {report.id}")
            continue  # Bỏ qua report nếu student không tồn tại

        # Resolve Link[Task]
        await report.task.fetch()
        if isinstance(report.task, Link):
            logger.error(f"Failed to resolve task for report {report.id}")
            continue  # Bỏ qua report nếu task không tồn tại

        result.append(ReportResponse(
            id=report.id,
            content=report.content,
            student={"id": str(report.student.id), "ho_ten": report.student.ho_ten},
            task={"id": str(report.task.id), "title": report.task.title},
            created_at=report.created_at
        ))
    return result

@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(report_id: str, report: ReportCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    db_report = await Report.get(report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Resolve Link[User]
    await db_report.student.fetch()
    if isinstance(db_report.student, Link):
        logger.error(f"Failed to resolve student for report {db_report.id}")
        raise HTTPException(status_code=404, detail="Student associated with report not found")

    if str(db_report.student.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")

    task = await Task.get(report.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Resolve assigned_students
    assigned_students = await task.fetch_link("assigned_students") or []
    if not assigned_students:
        logger.error(f"Task {task.id} has no assigned students")
        raise HTTPException(status_code=403, detail="No students assigned to this task")

    # Kiểm tra current_user có trong assigned_students hay không
    if str(current_user.id) not in [str(student.id) for student in assigned_students]:
        logger.info(f"User {current_user.id} is not authorized to report on task {task.id}")
        raise HTTPException(status_code=403, detail="Not authorized to report on this task")

    db_report.content = report.content
    db_report.task = task
    await db_report.save()
    logger.info(f"Updated report: {db_report.id}")
    
    # Resolve Link[Task] trước khi trả về
    await db_report.task.fetch()
    if isinstance(db_report.task, Link):
        logger.error(f"Failed to resolve task for report {db_report.id}")
        raise HTTPException(status_code=404, detail="Task associated with report not found")

    return ReportResponse(
        id=db_report.id,
        content=db_report.content,
        student={"id": str(db_report.student.id), "ho_ten": db_report.student.ho_ten},
        task={"id": str(db_report.task.id), "title": db_report.task.title},
        created_at=db_report.created_at
    )

@router.delete("/{report_id}")
async def delete_report(report_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    report = await Report.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Resolve Link[User]
    await report.student.fetch()
    if isinstance(report.student, Link):
        logger.error(f"Failed to resolve student for report {report.id}")
        raise HTTPException(status_code=404, detail="Student associated with report not found")

    if str(report.student.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")
    
    await report.delete()
    logger.info(f"Deleted report: {report_id}")
    return {"message": "Report deleted"}

