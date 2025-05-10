from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.report_model import Report
from models.task_model import Task
from models.user_model import User
from schemas.report_schemas import ReportCreate, ReportResponse
from schemas.pyobjectid_schemas import PyObjectId
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

@router.post("/", response_model=ReportResponse,
             description="Create a new report. Only students can create reports.",
            summary="Create a new report"
)
async def create_report(report: ReportCreate, current_user: User = Depends(get_current_user)):
    

    task = await Task.get(report.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")   

    new_report = Report(
        content=report.content,
        student=Link(current_user, document_class=User),
        task=Link(task, document_class=Task)
    )
    await new_report.insert()
    logger.info(f"Created new report: {new_report.id}")
    
    # Fetch student and task for response
    student = await new_report.student.fetch() if isinstance(new_report.student, Link) else new_report.student
    task = await new_report.task.fetch() if isinstance(new_report.task, Link) else new_report.task
    
    return ReportResponse(
        id=new_report.id,
        content=new_report.content,
        student={"id": str(student.id), "ho_ten": student.ho_ten},
        task={"id": str(task.id), "title": task.title},
        created_at=new_report.created_at
    )

@router.get("/{report_id}", response_model=ReportResponse,
             description="Get a report by ID. Only the student who created the report can view it.",
            summary="Get a report by ID"
)
async def get_reports(report_id: str, current_user: User = Depends(get_current_user)                      ):
    try:
        report_id_obj = PyObjectId.validate(report_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    
    try:
        report = await Report.get(report_id_obj)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")        
        task = await report.task.fetch() if isinstance(report.task, Link) else report.task
        if not task or isinstance(task, Link):
            logger.error(f"Failed to resolve task for report {report.id}")
            raise HTTPException(status_code=404, detail="Task associated with report not found")
        return ReportResponse(   
            _id = report.id,
            content = report.content,
            task = {"id": str(task.id), "title": task.title, "deadline": task.deadline},
            created_at = report.created_at
        )
    except Exception as e:
        logger.error(f"Error fetching report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=list[ReportResponse],
             description="Get all reports. Only the admin can view all reports.",
            summary="Get all reports"
)
async def get_all_reports(current_user: User = Depends(get_current_user),
                          skip: int=Query(0, ge=0, description="Number of reports to skip"), 
                          limit: int=Query(10, le=100, description="Maximum number of reports to return")):
    try:
        reports = await Report.find_all().skip(skip).limit(limit).to_list()
        results= []
        for report in reports:
            task = await report.task.fetch() if isinstance(report.task, Link) else report.task
            results.append(ReportResponse(
                id=report.id,
                content=report.content,
                task={"id": str(task.id), "title": task.title, "deadline": task.deadline},
                created_at=report.created_at
            ))

    except Exception as e:
        logger.error(f"Error fetching reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return results

@router.put("/{report_id}", response_model=ReportResponse,
            description="Update a report by ID. Only the student who created the report can update it.",
            summary="Update a report by ID")
async def update_report(report_id: str, report: ReportCreate, current_user: User = Depends(get_current_user)):

    db_report = await Report.get(report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Resolve Link[User]
    student = await db_report.student.fetch() if isinstance(db_report.student, Link) else db_report.student
    if not student or isinstance(student, Link):
        logger.error(f"Failed to resolve student for report {db_report.id}")
        raise HTTPException(status_code=404, detail="Student associated with report not found")

    if str(student.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")

    task = await Task.get(report.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

  

    db_report.content = report.content
    db_report.task = Link(task, document_class=Task)
    await db_report.save()
    logger.info(f"Updated report: {db_report.id}")
    
    # Resolve Link[Task] trước khi trả về
    task = await db_report.task.fetch() if isinstance(db_report.task, Link) else db_report.task
    if not task or isinstance(task, Link):
        logger.error(f"Failed to resolve task for report {db_report.id}")
        raise HTTPException(status_code=404, detail="Task associated with report not found")

    return ReportResponse(
        id=db_report.id,
        content=db_report.content,
        student={"id": str(student.id), "ho_ten": student.ho_ten},
        task={"id": str(task.id), "title": task.title},
        created_at=db_report.created_at
    )

@router.delete("/{report_id}",
               description="Delete a report by ID. Only the student who created the report can delete it.",
            summary="Delete a report by ID")
async def delete_report(report_id: str, current_user: User = Depends(get_current_user)):
    try:
        report_id_obj = PyObjectId.validate(report_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    try:
        report = await Report.get(report_id_obj)
        if not report:
            logger.error(f"Report with ID {report_id_obj} not found in database")
            raise HTTPException(status_code=404, detail="Report not found")

        # Thêm kiểm tra quyền (nếu cần)
        student = await report.student.fetch() if isinstance(report.student, Link) else report.student
        if str(student.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this report")

        await report.delete()
        logger.info(f"Deleted report: {report_id}")
        return {"message": "Report deleted"}
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")