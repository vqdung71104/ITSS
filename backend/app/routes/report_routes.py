from fastapi import APIRouter, Depends, HTTPException, status
from models.report_model import Report
from models.task_model import Task
from models.user_model import User
from schemas.report_schemas import ReportCreate, ReportResponse
from routes.user_routes import get_current_user

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
    
    assigned_students = await task.assigned_students.fetch() if task.assigned_students else []
    if current_user not in assigned_students:
        raise HTTPException(status_code=403, detail="Not authorized to report on this task")

    new_report = Report(
        content=report.content,
        student=current_user,
        task=task
    )
    await new_report.insert()
    return new_report

@router.get("/", response_model=list[ReportResponse])
async def get_reports(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    reports = await Report.find({"student.$id": current_user.id}).to_list()
    return reports

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
    
    assigned_students = await task.assigned_students.fetch() if task.assigned_students else []
    if current_user not in assigned_students:
        raise HTTPException(status_code=403, detail="Not authorized to report on this task")

    db_report.content = report.content
    db_report.task = task
    await db_report.save()
    return db_report

@router.delete("/{report_id}")
async def delete_report(report_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    report = await Report.get(report_id)
    if not report or str(report.student.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")
    
    await report.delete()
    return {"message": "Report deleted"}