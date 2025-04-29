from fastapi import APIRouter, Depends, HTTPException, status
from models.evaluation_model import Evaluation
from models.user_model import User
from models.project_model import Project
from schemas.evaluation_schemas import EvaluationCreate, EvaluationResponse
from routes.user_routes import get_current_user
from beanie import Link
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/evaluations",
    tags=["evaluations"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=EvaluationResponse)
async def create_evaluation(evaluation: EvaluationCreate, current_user: User = Depends(get_current_user)):
    # Kiểm tra student
    student = await User.get(evaluation.student_id)
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    # Kiểm tra project
    project = await Project.get(evaluation.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Kiểm tra mentor reference trước khi fetch
    if not project.mentor.ref or not project.mentor.ref.id:
        logger.error(f"Invalid mentor reference for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    # Fetch mentor để kiểm tra quyền
    mentor = await project.mentor.fetch()
    if not mentor:
        logger.error(f"Failed to resolve mentor for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if str(mentor.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to create evaluation for this project")

    # Tạo evaluation mới
    new_evaluation = Evaluation(
        evaluator=Link(current_user, document_class=User),
        student=Link(student, document_class=User),
        project=Link(project, document_class=Project),
        score=evaluation.score,
        comment=evaluation.comment
    )
    await new_evaluation.insert()
    logger.info(f"Created new evaluation: {new_evaluation.id}")

    # Trả về response mà không cần fetch lại (vì đã có dữ liệu cần thiết)
    return EvaluationResponse(
        id=new_evaluation.id,
        evaluator={"id": str(current_user.id), "ho_ten": current_user.ho_ten},
        student={"id": str(student.id), "ho_ten": student.ho_ten},
        project={"id": str(project.id), "title": project.title},
        score=new_evaluation.score,
        comment=new_evaluation.comment
    )

@router.get("/{project_id}", response_model=list[EvaluationResponse])
async def get_evaluations(project_id: str, current_user: User = Depends(get_current_user)):
    # Kiểm tra project
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Kiểm tra mentor reference trước khi fetch
    if not project.mentor.ref or not project.mentor.ref.id:
        logger.error(f"Invalid mentor reference for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    # Fetch mentor để kiểm tra quyền
    mentor = await project.mentor.fetch()
    if not mentor:
        logger.error(f"Failed to resolve mentor for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if str(mentor.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view evaluations for this project")

    # Lấy danh sách evaluations
    evaluations = await Evaluation.find({"project.$id": project.id}).to_list()
    result = []
    for evaluation in evaluations:
        # Chỉ lấy ID từ Link, không fetch nếu không cần thiết
        evaluator_id = evaluation.evaluator.ref.id if evaluation.evaluator.ref else None
        student_id = evaluation.student.ref.id if evaluation.student.ref else None
        project_id = evaluation.project.ref.id if evaluation.project.ref else None

        # Kiểm tra tính hợp lệ của các tham chiếu
        if not evaluator_id or evaluator_id != current_user.id:
            logger.error(f"Invalid evaluator reference for evaluation {evaluation.id}")
            continue
        if not student_id:
            logger.error(f"Invalid student reference for evaluation {evaluation.id}")
            continue
        if not project_id:
            logger.error(f"Invalid project reference for evaluation {evaluation.id}")
            continue

        # Fetch student để lấy ho_ten
        student = await evaluation.student.fetch()
        if not student:
            logger.error(f"Failed to resolve student for evaluation {evaluation.id}")
            continue

        result.append(EvaluationResponse(
            id=evaluation.id,
            evaluator={"id": str(current_user.id), "ho_ten": current_user.ho_ten},
            student={"id": str(student.id), "ho_ten": student.ho_ten},
            project={"id": str(project.id), "title": project.title},
            score=evaluation.score,
            comment=evaluation.comment
        ))
    return result

@router.put("/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(evaluation_id: str, evaluation: EvaluationCreate, current_user: User = Depends(get_current_user)):
    # Kiểm tra evaluation
    db_evaluation = await Evaluation.get(evaluation_id)
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    # Kiểm tra evaluator trước khi fetch
    evaluator_id = None
    if isinstance(db_evaluation.evaluator, Link):
        evaluator_id = db_evaluation.evaluator.ref.id if db_evaluation.evaluator.ref else None
    elif isinstance(db_evaluation.evaluator, User):
        evaluator_id = db_evaluation.evaluator.id

    if not evaluator_id:
        logger.error(f"Invalid evaluator reference for evaluation {db_evaluation.id}")
        raise HTTPException(status_code=404, detail="Evaluator associated with evaluation not found")

    # Fetch evaluator để kiểm tra quyền
    evaluator = await db_evaluation.evaluator.fetch()
    if not evaluator:
        logger.error(f"Failed to resolve evaluator for evaluation {db_evaluation.id}")
        raise HTTPException(status_code=404, detail="Evaluator associated with evaluation not found")

    if str(evaluator.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this evaluation")

    # Kiểm tra student
    student = await User.get(evaluation.student_id)
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    # Kiểm tra project
    project = await Project.get(evaluation.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Kiểm tra mentor reference trước khi fetch
    if not project.mentor.ref or not project.mentor.ref.id:
        logger.error(f"Invalid mentor reference for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    # Fetch mentor để kiểm tra quyền
    mentor = await project.mentor.fetch()
    if not mentor:
        logger.error(f"Failed to resolve mentor for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if str(mentor.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update evaluations for this project")

    # Cập nhật evaluation
    db_evaluation.student = Link(student, document_class=User)
    db_evaluation.project = Link(project, document_class=Project)
    db_evaluation.score = evaluation.score
    db_evaluation.comment = evaluation.comment
    await db_evaluation.save()
    logger.info(f"Updated evaluation: {db_evaluation.id}")

    # Trả về response mà không cần fetch lại
    return EvaluationResponse(
        id=db_evaluation.id,
        evaluator={"id": str(current_user.id), "ho_ten": current_user.ho_ten},
        student={"id": str(student.id), "ho_ten": student.ho_ten},
        project={"id": str(project.id), "title": project.title},
        score=db_evaluation.score,
        comment=db_evaluation.comment
    )

@router.delete("/{evaluation_id}")
async def delete_evaluation(evaluation_id: str, current_user: User = Depends(get_current_user)):
    # Kiểm tra evaluation
    evaluation = await Evaluation.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    # Kiểm tra evaluator trước khi fetch
    evaluator_id = None
    if isinstance(evaluation.evaluator, Link):
        evaluator_id = evaluation.evaluator.ref.id if evaluation.evaluator.ref else None
    elif isinstance(evaluation.evaluator, User):
        evaluator_id = evaluation.evaluator.id

    if not evaluator_id:
        logger.error(f"Invalid evaluator reference for evaluation {evaluation.id}")
        raise HTTPException(status_code=404, detail="Evaluator associated with evaluation not found")

    # Fetch evaluator để kiểm tra quyền
    evaluator = await evaluation.evaluator.fetch()
    if not evaluator:
        logger.error(f"Failed to resolve evaluator for evaluation {evaluation.id}")
        raise HTTPException(status_code=404, detail="Evaluator associated with evaluation not found")

    if str(evaluator.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this evaluation")
    
    await evaluation.delete()
    logger.info(f"Deleted evaluation: {evaluation_id}")
    return {"message": "Evaluation deleted"}