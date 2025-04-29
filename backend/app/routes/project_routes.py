from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from models.project_model import Project
from models.user_model import User
from schemas.project_schemas import ProjectCreate, ProjectResponse, ProjectListResponse, PyObjectId
from routes.user_routes import get_current_mentor
from beanie import Link
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

@router.get("/list", response_model=List[ProjectListResponse])
async def get_projects(current_user: User = Depends(get_current_mentor)):
    try:
        projects = await Project.find({"mentor.$id": current_user.id}).to_list()
        if not projects:
            logger.info(f"No projects found for mentor {current_user.id}")
            raise HTTPException(status_code=404, detail="No projects found for this mentor")
        
        # Fetch groups for each project
        project_responses = []
        for project in projects:
            # Truy cập trực tiếp mentor.ref.id giống như trong task_routes.py
            if not hasattr(project.mentor, "ref") or not hasattr(project.mentor.ref, "id"):
                logger.error(f"Invalid mentor reference for project {project.id}")
                continue
                
            groups = await project.fetch_link("groups") or []
            project_responses.append(ProjectListResponse(
                id=str(project.id),
                title=project.title,
                description=project.description,
                mentor_id=str(project.mentor.ref.id),
                group_ids=[str(group.id) for group in groups] if groups else []
            ))
        
        if not project_responses:
            logger.info(f"No valid projects found for mentor {current_user.id} after filtering")
            raise HTTPException(status_code=404, detail="No valid projects found for this mentor")
        
        return project_responses
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=ProjectResponse)
async def get_project(
    project_id: Optional[str] = Query(None, description="Project ID to search for"),
    title: Optional[str] = Query(None, description="Project title to search for"),
    description: Optional[str] = Query(None, description="Project description to search for"),
    current_user: User = Depends(get_current_mentor)
):
    try:
        if not project_id and not title and not description:
            raise HTTPException(status_code=400, detail="At least one search criterion must be provided")

        query = {"mentor.$id": current_user.id}

        if project_id:
            try:
                project_id_obj = PyObjectId.validate(project_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid project_id format")
            query["_id"] = project_id_obj

        if title:
            query["title"] = {"$regex": title, "$options": "i"}

        if description:
            query["description"] = {"$regex": description, "$options": "i"}

        project = await Project.find_one(query)
        if not project:
            logger.info(f"Project not found with query: {query}")
            raise HTTPException(status_code=404, detail="Project not found")

        # Truy cập trực tiếp mentor.ref.id giống như trong task_routes.py
        if not hasattr(project.mentor, "ref") or not hasattr(project.mentor.ref, "id"):
            logger.error(f"Invalid mentor reference for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        # Fetch groups
        groups = await project.fetch_link("groups") or []
        
        return ProjectResponse(
            id=str(project.id),
            title=project.title,
            description=project.description,
            mentor_id=str(project.mentor.ref.id),
            group_ids=[str(group.id) for group in groups] if groups else []
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
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

        # Resolve Link[User] for mentor if it's a Link
        mentor_id = None
        if isinstance(db_project.mentor, Link):
            await db_project.mentor.fetch()
            if isinstance(db_project.mentor, Link):
                logger.error(f"Failed to resolve mentor for project {db_project.id}")
                raise HTTPException(status_code=404, detail="Mentor associated with project not found")
            mentor_id = str(db_project.mentor.id)
        else:
            mentor_id = str(db_project.mentor.id)

        if mentor_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        db_project.title = project.title
        db_project.description = project.description
        await db_project.save()

        # Fetch groups
        groups = await db_project.fetch_link("groups") or []
        
        logger.info(f"Updated project: {db_project.id}")
        
        return ProjectResponse(
            id=str(db_project.id),
            title=db_project.title,
            description=db_project.description,
            mentor_id=mentor_id,
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

        # Truy cập trực tiếp mentor.ref.id giống như trong task_routes.py
        if not hasattr(project.mentor, "ref") or not hasattr(project.mentor.ref, "id"):
            logger.error(f"Invalid mentor reference for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(project.mentor.ref.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Fetch and delete all groups and their tasks
        groups = await project.fetch_link("groups") or []
        for group in groups:
            # Fetch and delete all tasks in the group
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