from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from schemas.user_schemas import UserResponse
from schemas.group_schemas import GroupResponse
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
            image=project.image,
            description=project.description,
            mentor=Link(current_user, document_class=User),
            groups=[]
        )
        await new_project.insert()
        
        logger.info(f"Created new project: {new_project.id}")
        
        return ProjectResponse(
            _id=str(new_project.id),
            title=new_project.title,
            image=new_project.image,
            description=new_project.description,
            mentor_id=str(current_user.id),
            group_ids=[]
        )
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/all")
async def get_all_projects(
    skip: int = 0, 
    limit: int = 50, 
):
    try:
        projects = await Project.find_all().skip(skip).limit(limit).to_list()
        result = []

        for project in projects:
            mentor_obj = None
            if project.mentor:
                try:
                    mentor_obj = await project.mentor.fetch() if isinstance(project.mentor, Link) else project.mentor
                except Exception:
                    logger.warning(f"Could not fetch mentor for project {project.id}")
            
            result.append({
                "_id": str(project.id),
                "title": project.title,
                "image": getattr(project, "image", None),
                "description": project.description,
                "mentor": mentor_obj,
            })

        return result
    except Exception as e:
        logger.error(f"Error fetching all projects: {repr(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{project_id}", response_model=ProjectListResponse)
async def get_project_by_id(
    project_id: str,    
):
    try:
        project_id_obj = PyObjectId.validate(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")

    try:
        project = await Project.get(project_id_obj)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch mentor
        mentor = await project.mentor.fetch() if isinstance(project.mentor, Link) else project.mentor

        # Fetch groups
        groups = await project.fetch_link("groups") or []

        # Convert to response schema
        return ProjectListResponse(
            _id=project.id,
            title=project.title,
            image=project.image,
            description=project.description,
            mentor=UserResponse(**mentor.model_dump()) if mentor else None,
            groups=[GroupResponse(**group.model_dump()) for group in groups]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project by ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{project_id}", response_model=ProjectListResponse)
async def update_project(
    project_id: str,
    project: ProjectCreate,
    current_user: User = Depends(get_current_mentor)
):
    try:
        # Validate project_id
        project_id_obj = PyObjectId.validate(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")

    try:
        # Lấy project từ DB
        db_project = await Project.get(project_id_obj)
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Kiểm tra quyền
        await db_project.fetch_link("mentor")
        if str(db_project.mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Cập nhật project
        db_project.title = project.title
        db_project.description = project.description
        await db_project.save()

        # Fetch mentor
        mentor = await db_project.mentor.fetch() if isinstance(db_project.mentor, Link) else db_project.mentor

        # Fetch groups
        groups = await db_project.fetch_link("groups") or []

        logger.info(f"Updated project: {db_project.id}")

        return ProjectListResponse(
            _id=db_project.id,
            title=db_project.title,
            image=db_project.image,
            description=db_project.description,
            mentor=UserResponse(**mentor.model_dump()) if mentor else None,
            groups=[GroupResponse(**group.model_dump()) for group in groups]
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