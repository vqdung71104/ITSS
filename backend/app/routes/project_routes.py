from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from models.project_model import Project
from models.user_model import User
from schemas.project_schemas import ProjectCreate, ProjectResponse, ProjectListResponse
from schemas.pyobjectid_schemas import PyObjectId
from routes.user_routes import get_current_mentor
from beanie import Link
from bson import ObjectId
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_mentor)):
    try:
        new_project = Project(
            title=project.title,
            description=project.description,
            mentor=Link(current_user, document_class=User),
            groups=[]
        )
        await new_project.insert()
        
        logger.info(f"Created new project: {new_project.id}")
        
        return ProjectResponse(
            id=str(new_project.id),
            title=new_project.title,
            description=new_project.description,
            mentor_id=str(current_user.id),
            group_ids=[]
        )
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/all", response_model=List[dict])
async def get_all_projects(current_user: User = Depends(get_current_mentor)):
    try:
        projects = await Project.find_all().to_list()
        result = []
        
        for project in projects:
            mentor_name = None
            if project.mentor:
                # Fetch mentor if it is a Link
                mentor = await project.mentor.fetch() if isinstance(project.mentor, Link) else project.mentor
                if mentor:
                    mentor_name = mentor.ho_ten
                else:
                    logger.warning(f"Failed to fetch mentor for project {project.id}")
            
            result.append({
                "id": str(project.id),
                "title": project.title,
                "description": project.description,
                "mentor_name": mentor_name,
            })
        
        return result
    except Exception as e:
        logger.error(f"Error fetching all projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(project_id: str, current_user: User = Depends(get_current_mentor)):
    try:
        # Validate the project_id format
        project_id_obj = PyObjectId.validate(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")

    try:
        # Fetch the project from the database
        project = await Project.get(project_id_obj)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Ensure the mentor is loaded
        await project.fetch_link("mentor")

        # Check if the current user is the mentor of the project
        if str(project.mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Fetch linked groups
        groups = await project.fetch_link("groups") or []

        return ProjectResponse(
            id=str(project.id),
            title=project.title,
            description=project.description,
            mentor_id=str(project.mentor.id),
            group_ids=[str(group.id) for group in groups] if groups else []
        )
    except Exception as e:
        logger.error(f"Error fetching project by ID: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project: ProjectCreate, current_user: User = Depends(get_current_mentor)):
    try:
        project_id_obj = PyObjectId.validate(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")

    try:
        db_project = await Project.get(project_id_obj)
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        await db_project.fetch_link("mentor")  # Ensure mentor is loaded

        if str(db_project.mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        db_project.title = project.title
        db_project.description = project.description
        await db_project.save()

        groups = await db_project.fetch_link("groups") or []
        
        logger.info(f"Updated project: {db_project.id}")
        
        return ProjectResponse(
            id=str(db_project.id),
            title=db_project.title,
            description=db_project.description,
            mentor_id=str(db_project.mentor.id),
            group_ids=[str(group.id) for group in groups] if groups else []
        )
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_mentor)):
    try:
        project_id_obj = PyObjectId.validate(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")

    try:
        project = await Project.get(project_id_obj)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        await project.fetch_link("mentor")  # Ensure mentor is loaded
        if not project.mentor or not project.mentor.id:
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(project.mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        groups = await project.fetch_link("groups") or []
        for group in groups:
            tasks = await group.fetch_link("allTasks") or []
            for task in tasks:
                await task.delete()
            await group.delete()
        
        await project.delete()
        
        logger.info(f"Deleted project: {project_id}")
        
        return {"message": "Project deleted"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")