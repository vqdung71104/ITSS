from fastapi import APIRouter, Depends, HTTPException, status
from models.evaluation_model import Evaluation
from models.user_model import User
from models.project_model import Project
from schemas.evaluation_schemas import EvaluationCreate, EvaluationResponse
from routes.user_routes import get_current_mentor

router = APIRouter(
    prefix="/evaluations",
    tags=["evaluations"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=EvaluationResponse)
async def create_evaluation(evaluation: EvaluationCreate, current_user: User = Depends(get_current_mentor)):
    student = await User.get(evaluation.student_id)
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    project = await Project.get(evaluation.project_id)
    if not project or str(project.mentor.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")

    new_evaluation = Evaluation(
        evaluator=current_user,
        student=student,
        project=project,
        score=evaluation.score,
        comment=evaluation.comment
    )
    await new_evaluation.insert()
    return new_evaluation

@router.get("/{project_id}", response_model=list[EvaluationResponse])
async def get_evaluations(project_id: str, current_user: User = Depends(get_current_mentor)):
    project = await Project.get(project_id)
    if not project or str(project.mentor.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")

    evaluations = await Evaluation.find({"project.$id": project.id}).to_list()
    return evaluations

@router.put("/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(evaluation_id: str, evaluation: EvaluationCreate, current_user: User = Depends(get_current_mentor)):
    db_evaluation = await Evaluation.get(evaluation_id)
    if not db_evaluation or str(db_evaluation.evaluator.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Evaluation not found")

    student = await User.get(evaluation.student_id)
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    project = await Project.get(evaluation.project_id)
    if not project or str(project.mentor.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")

    db_evaluation.student = student
    db_evaluation.project = project
    db_evaluation.score = evaluation.score
    db_evaluation.comment = evaluation.comment
    await db_evaluation.save()
    return db_evaluation

@router.delete("/{evaluation_id}")
async def delete_evaluation(evaluation_id: str, current_user: User = Depends(get_current_mentor)):
    evaluation = await Evaluation.get(evaluation_id)
    if not evaluation or str(evaluation.evaluator.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    await evaluation.delete()
    return {"message": "Evaluation deleted"}