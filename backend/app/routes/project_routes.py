from fastapi import APIRouter, Depends, HTTPException, status
from models.project_model import Project
from models.user_model import User
from schemas.project_schemas import ProjectCreate, ProjectResponse
from routes.user_routes import get_current_admin

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_admin)):
    new_project = Project(
        title=project.title,
        description=project.description,
        mentor=current_user,
        groups=[]
    )
    await new_project.insert()
    return new_project

@router.get("/", response_model=list[ProjectResponse])
async def get_projects(current_user: User = Depends(get_current_admin)):
    projects = await Project.find({"mentor.$id": current_user.id}).to_list()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: User = Depends(get_current_admin)):
    project = await Project.get(project_id)
    if not project or str(project.mentor.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project: ProjectCreate, current_user: User = Depends(get_current_admin)):
    db_project = await Project.get(project_id)
    if not db_project or str(db_project.mentor.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.title = project.title
    db_project.description = project.description
    await db_project.save()
    return db_project

@router.delete("/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_admin)):
    project = await Project.get(project_id)
    if not project or str(project.mentor.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Xóa các nhóm liên quan
    groups = await project.groups.fetch() if project.groups else []
    for group in groups:
        await group.delete()
    
    await project.delete()
    return {"message": "Project deleted"}