from fastapi import APIRouter, Depends, HTTPException, status
from models.evaluation_model import Evaluation
from models.user_model import User
from models.project_model import Project
from schemas.evaluation_schemas import EvaluationCreate, EvaluationResponse, PyObjectId
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
    # Validate and get student
    try:
        student_id = PyObjectId.validate(evaluation.student_id)
        student = await User.get(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student_id format")
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    # Validate and get project
    try:
        project_id = PyObjectId.validate(evaluation.project_id)
        project = await Project.get(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check mentor (handle both Link and User)
    mentor = None
    if isinstance(project.mentor, Link):
        if not project.mentor.ref or not project.mentor.ref.id:
            logger.error(f"Invalid mentor reference for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")
        mentor = await project.mentor.fetch()
    elif isinstance(project.mentor, User):
        mentor = project.mentor
    else:
        logger.error(f"Invalid mentor type for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if not mentor:
        logger.error(f"Failed to resolve mentor for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if str(mentor.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to create evaluation for this project")

    # Create new evaluation
    new_evaluation = Evaluation(
        evaluator=Link(current_user, document_class=User),
        student=Link(student, document_class=User),
        project=Link(project, document_class=Project),
        score=evaluation.score,
        comment=evaluation.comment
    )
    await new_evaluation.insert()
    logger.info(f"Created new evaluation: {new_evaluation.id}")

    # Return response without fetching again
    return EvaluationResponse(
        id=str(new_evaluation.id),
        evaluator={"id": str(current_user.id), "ho_ten": current_user.ho_ten},
        student={"id": str(student.id), "ho_ten": student.ho_ten},
        project={"id": str(project.id), "title": project.title},
        score=new_evaluation.score,
        comment=new_evaluation.comment
    )


@router.get("/{project_id}", response_model=list[EvaluationResponse])
async def get_evaluations(project_id: str, current_user: User = Depends(get_current_user)):
    # Validate and get project
    try:
        project_id_obj = PyObjectId.validate(project_id)
        project = await Project.get(project_id_obj)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check mentor (handle both Link and User)
    mentor = None
    if isinstance(project.mentor, Link):
        if not project.mentor.ref or not project.mentor.ref.id:
            logger.error(f"Invalid mentor reference for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")
        mentor = await project.mentor.fetch()
    elif isinstance(project.mentor, User):
        mentor = project.mentor
    else:
        logger.error(f"Invalid mentor type for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if not mentor:
        logger.error(f"Failed to resolve mentor for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if str(mentor.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view evaluations for this project")

    # Get evaluations
    evaluations = await Evaluation.find({"project.$id": project.id}).to_list()
    result = []
    for evaluation in evaluations:
        # Get evaluator ID (handle both Link and User)
        evaluator_id = None
        if isinstance(evaluation.evaluator, Link):
            evaluator_id = evaluation.evaluator.ref.id if evaluation.evaluator.ref else None
        elif isinstance(evaluation.evaluator, User):
            evaluator_id = evaluation.evaluator.id

        if not evaluator_id or str(evaluator_id) != str(current_user.id):
            logger.error(f"Invalid evaluator reference for evaluation {evaluation.id}")
            continue

        # Get student ID
        student_id = None
        if isinstance(evaluation.student, Link):
            student_id = evaluation.student.ref.id if evaluation.student.ref else None
        elif isinstance(evaluation.student, User):
            student_id = evaluation.student.id

        if not student_id:
            logger.error(f"Invalid student reference for evaluation {evaluation.id}")
            continue

        # Get project ID
        project_id_eval = None
        if isinstance(evaluation.project, Link):
            project_id_eval = evaluation.project.ref.id if evaluation.project.ref else None
        elif isinstance(evaluation.project, Project):
            project_id_eval = evaluation.project.id

        if not project_id_eval:
            logger.error(f"Invalid project reference for evaluation {evaluation.id}")
            continue

        # Fetch student for response
        student = await evaluation.student.fetch() if isinstance(evaluation.student, Link) else evaluation.student
        if not student:
            logger.error(f"Failed to resolve student for evaluation {evaluation.id}")
            continue

        result.append(EvaluationResponse(
            id=str(evaluation.id),
            evaluator={"id": str(current_user.id), "ho_ten": current_user.ho_ten},
            student={"id": str(student.id), "ho_ten": student.ho_ten},
            project={"id": str(project.id), "title": project.title},
            score=evaluation.score,
            comment=evaluation.comment
        ))
    return result

@router.put("/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(evaluation_id: str, evaluation: EvaluationCreate, current_user: User = Depends(get_current_user)):
    # Validate and get evaluation
    try:
        evaluation_id_obj = PyObjectId.validate(evaluation_id)
        db_evaluation = await Evaluation.get(evaluation_id_obj)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid evaluation_id format")
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    # Check evaluator (handle both Link and User)
    evaluator_id = None
    if isinstance(db_evaluation.evaluator, Link):
        evaluator_id = db_evaluation.evaluator.ref.id if db_evaluation.evaluator.ref else None
    elif isinstance(db_evaluation.evaluator, User):
        evaluator_id = db_evaluation.evaluator.id

    if not evaluator_id:
        logger.error(f"Invalid evaluator reference for evaluation {db_evaluation.id}")
        raise HTTPException(status_code=404, detail="Evaluator associated with evaluation not found")

    # Fetch evaluator only if it is a Link
    evaluator = db_evaluation.evaluator if isinstance(db_evaluation.evaluator, User) else await db_evaluation.evaluator.fetch()
    if not evaluator:
        logger.error(f"Failed to resolve evaluator for evaluation {db_evaluation.id}")
        raise HTTPException(status_code=404, detail="Evaluator associated with evaluation not found")

    if str(evaluator.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this evaluation")

    # Validate and get student
    try:
        student_id = PyObjectId.validate(evaluation.student_id)
        student = await User.get(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student_id format")
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    # Validate and get project
    try:
        project_id = PyObjectId.validate(evaluation.project_id)
        project = await Project.get(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check mentor (handle both Link and User)
    mentor = None
    if isinstance(project.mentor, Link):
        if not project.mentor.ref or not project.mentor.ref.id:
            logger.error(f"Invalid mentor reference for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")
        mentor = await project.mentor.fetch()
    elif isinstance(project.mentor, User):
        mentor = project.mentor
    else:
        logger.error(f"Invalid mentor type for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if not mentor:
        logger.error(f"Failed to resolve mentor for project {project.id}")
        raise HTTPException(status_code=404, detail="Mentor associated with project not found")

    if str(mentor.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update evaluations for this project")

    # Update evaluation
    db_evaluation.student = Link(student, document_class=User)
    db_evaluation.project = Link(project, document_class=Project)
    db_evaluation.score = evaluation.score
    db_evaluation.comment = evaluation.comment
    await db_evaluation.save()
    logger.info(f"Updated evaluation: {db_evaluation.id}")

    # Return response
    return EvaluationResponse(
        id=str(db_evaluation.id),
        evaluator={"id": str(current_user.id), "ho_ten": current_user.ho_ten},
        student={"id": str(student.id), "ho_ten": student.ho_ten},
        project={"id": str(project.id), "title": project.title},
        score=db_evaluation.score,
        comment=db_evaluation.comment
    )

@router.delete("/{evaluation_id}")
async def delete_evaluation(evaluation_id: str, current_user: User = Depends(get_current_user)):
    # Validate and get evaluation
    try:
        evaluation_id_obj = PyObjectId.validate(evaluation_id)
        evaluation = await Evaluation.get(evaluation_id_obj)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid evaluation_id format")
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    # Check evaluator (handle both Link and User)
    evaluator_id = None
    if isinstance(evaluation.evaluator, Link):
        evaluator_id = evaluation.evaluator.ref.id if evaluation.evaluator.ref else None
    elif isinstance(evaluation.evaluator, User):
        evaluator_id = evaluation.evaluator.id

    if not evaluator_id:
        logger.error(f"Invalid evaluator reference for evaluation {evaluation.id}")
        raise HTTPException(status_code=404, detail="Evaluator associated with evaluation not found")

    # Fetch evaluator only if it is a Link
    evaluator = evaluation.evaluator if isinstance(evaluation.evaluator, User) else await evaluation.evaluator.fetch()
    if not evaluator:
        logger.error(f"Failed to resolve evaluator for evaluation {evaluation.id}")
        raise HTTPException(status_code=404, detail="Evaluator associated with evaluation not found")

    if str(evaluator.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this evaluation")

    await evaluation.delete()
    logger.info(f"Deleted evaluation: {evaluation_id}")
    return {"message": "Evaluation deleted"}