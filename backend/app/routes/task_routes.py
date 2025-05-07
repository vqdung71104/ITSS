from fastapi import APIRouter, Depends, HTTPException, status
from models.task_model import Task
from models.group_model import Group
from models.user_model import User
from models.project_model import Project
from schemas.task_schemas import TaskCreate, TaskResponse
from schemas.pyobjectid_schemas import PyObjectId
from routes.user_routes import get_current_user
from beanie import Link
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}} 
)

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    try:
        group = await Group.get(task.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if str(group.leaders.ref.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        project = await group.project.fetch()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Validate and get assigned students
        assigned_students = []
        for student_id in task.assigned_student_ids:
            student = await User.get(student_id)
            if not student or student.role != "student":
                raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
            assigned_students.append(Link(student, document_class=User))

        # Create new task
        new_task = Task(
            title=task.title,
            description=task.description,
            group=Link(group, document_class=Group),
            assigned_students=assigned_students,
            status=task.status,
            deadline=task.deadline,
            related_to_project=Link(project, document_class=Project)
        )
        await new_task.save()

        # Add task to group
        group.allTasks = await group.fetch_link("allTasks") or []
        group.allTasks.append(Link(new_task, document_class=Task))
        await group.save()
        
        # Prepare response data
        group_data = {"id": str(group.id), "name": group.name}
        project_data = {"id": str(project.id), "title": project.title}
        
        students_data = []
        for student_link in new_task.assigned_students:
            if isinstance(student_link, Link):
                student = await student_link.fetch()
            else:
                student = student_link
                students_data.append({"id": str(student.id), "ho_ten": student.ho_ten})

        logger.info(f"Created new task: {new_task.id}")
        
        return TaskResponse(
            id=str(new_task.id),
            title=new_task.title,
            description=new_task.description,
            group=group_data,
            assigned_students=students_data,
            status=new_task.status,
            deadline=new_task.deadline,
            related_to_project=project_data
        )
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{group_id}", response_model=list[TaskResponse])
async def get_tasks(group_id: str, current_user: User = Depends(get_current_user)):
    try:
        # Validate the group_id format
        logger.info(f"Group ID: {group_id}")
        try:
            group_id_obj = PyObjectId.validate(group_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid group_id format")

        # Fetch the group from the database
        logger.info(f"Group ID Object: {group_id_obj}")
        group = await Group.get(group_id_obj)
        logger.info(f"Group: {group}")
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Check authorization (handle both Link and User)
        leader_id = None
        if isinstance(group.leaders, Link):
            leader = await group.leaders.fetch()
            leader_id = str(leader.id) if leader else None
        elif isinstance(group.leaders, User):
            leader_id = str(group.leaders.id)
        if not leader_id or leader_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Fetch all tasks associated with the group
        logger.info(f"Fetching tasks for group ID: {group_id_obj}")
        tasks = await Task.find({"group.$id": group_id_obj}).to_list()
        logger.info(f"Tasks found: {tasks}")
        
        # If no tasks found, check group.allTasks for debugging
        if not tasks:
            logger.info(f"No tasks found for group ID: {group_id_obj}. Checking group.allTasks...")
            group_tasks = await group.fetch_link("allTasks") or []
            logger.info(f"Group.allTasks: {group_tasks}")

        # Prepare the response
        task_responses = []
        for task in tasks:
            # Fetch related data
            project = await task.related_to_project.fetch()
            students = await task.fetch_link("assigned_students")
            
            task_responses.append(TaskResponse(
                id=str(task.id),
                title=task.title,
                description=task.description,
                group={"id": str(group.id), "name": group.name},
                assigned_students=[{"id": str(s.id), "ho_ten": s.ho_ten} for s in students] if students else [],
                status=task.status,
                deadline=task.deadline,
                related_to_project={"id": str(project.id), "title": project.title} if project else None
            ))

        return task_responses
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskCreate, current_user: User = Depends(get_current_user)):
    try:
        # Lấy task từ database
        db_task = await Task.get(task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Lấy group liên quan
        group = await Group.get(task.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if str(group.leaders.ref.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Lấy project liên quan
        project = await group.project.fetch()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Lấy danh sách students cũ
        old_students = []
        if db_task.assigned_students:
            for student_ref in db_task.assigned_students:
                if isinstance(student_ref, Link):
                    student = await student_ref.fetch()
                else:
                    student = student_ref
                old_students.append(student)

        # Thêm task vào sinh viên mới
        assigned_students = []
        for student_id in task.assigned_student_ids:
            student = await User.get(student_id)
            if not student or student.role != "student":
                raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
            assigned_students.append(Link(student, document_class=User))

        # Cập nhật task
        db_task.title = task.title
        db_task.description = task.description
        db_task.group = Link(group, document_class=Group)
        db_task.assigned_students = assigned_students
        db_task.status = task.status
        db_task.deadline = task.deadline
        db_task.related_to_project = Link(project, document_class=Project)
        await db_task.save()

        # Chuyển đổi dữ liệu để trả về
        group_data = {
            "id": str(group.id),
            "name": group.name
        }
        project_data = {
            "id": str(project.id),
            "title": project.title
        }
        
        # Lấy danh sách students mới
        students_data = []
        for student_ref in db_task.assigned_students:
            if isinstance(student_ref, Link):
                student = await student_ref.fetch()
            else:
                student = student_ref
            students_data.append({"id": str(student.id), "ho_ten": student.ho_ten})

        logger.info(f"Updated task: {db_task.id}")
        
        return TaskResponse(
            id=str(db_task.id),
            title=db_task.title,
            description=db_task.description,
            group=group_data,
            assigned_students=students_data,
            status=db_task.status,
            deadline=db_task.deadline,
            related_to_project=project_data
        )
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    try:
        task = await Task.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Fetch group if task.group is a Link, otherwise use it directly
        group = None
        if isinstance(task.group, Link):
            group = await task.group.fetch()
        elif isinstance(task.group, Group):
            group = task.group
        else:
            raise HTTPException(status_code=404, detail="Group associated with task not found")

        if not group or str(group.leaders.ref.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Remove task from group
        group.allTasks = await group.fetch_link("allTasks") or []
        group.allTasks = [t for t in group.allTasks if str(t.ref.id) != task_id]
        await group.save()

        # Delete the task
        await task.delete()
        
        logger.info(f"Deleted task: {task_id}")
        
        return {"message": "Task deleted"}
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")