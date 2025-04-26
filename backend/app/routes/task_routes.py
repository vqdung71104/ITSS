from fastapi import APIRouter, Depends, HTTPException, status
from models.task_model import Task
from models.group_model import Group
from models.user_model import User
from models.project_model import Project
from schemas.task_schemas import TaskCreate, TaskResponse
from routes.user_routes import get_current_mentor

#create router
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}} 
)


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_mentor)):
    group = await Group.get(task.group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if str(group.leaders.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    project = await group.project.fetch()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    assigned_students = []
    for student_id in task.assigned_student_ids:
        student = await User.get(student_id)
        if not student or student.role != "student":
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        assigned_students.append(student)

    new_task = Task(
        title=task.title,
        description=task.description,
        group=group,
        assigned_students=assigned_students,
        status=task.status,
        deadline=task.deadline,
        related_to_project=project
    )
    await new_task.insert()

    # Thêm task vào nhóm
    if not group.allTasks:
        group.allTasks = []
    group.allTasks.append(new_task)
    await group.save()

    # Thêm task vào sinh viên
    for student in assigned_students:
        if not student.tasks:
            student.tasks = []
        student.tasks.append(new_task)
        await student.save()

    return new_task

@router.get("/{group_id}", response_model=list[TaskResponse])
async def get_tasks(group_id: str, current_user: User = Depends(get_current_mentor)):
    group = await Group.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if str(group.leaders.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    tasks = await Task.find({"group.$id": group.id}).to_list()
    return tasks

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskCreate, current_user: User = Depends(get_current_mentor)):
    db_task = await Task.get(task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    group = await Group.get(task.group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if str(group.leaders.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    project = await group.project.fetch()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Xóa task khỏi sinh viên cũ
    old_students = await db_task.assigned_students.fetch() if db_task.assigned_students else []
    for student in old_students:
        if student.tasks:
            student.tasks = [t for t in student.tasks if str(t.id) != task_id]
            await student.save()

    # Thêm task vào sinh viên mới
    assigned_students = []
    for student_id in task.assigned_student_ids:
        student = await User.get(student_id)
        if not student or student.role != "student":
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        assigned_students.append(student)
        if not student.tasks:
            student.tasks = []
        student.tasks.append(db_task)
        await student.save()

    # Cập nhật task
    db_task.title = task.title
    db_task.description = task.description
    db_task.group = group
    db_task.assigned_students = assigned_students
    db_task.status = task.status
    db_task.deadline = task.deadline
    db_task.related_to_project = project
    await db_task.save()

    return db_task

@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_mentor)):
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    group = await task.group.fetch()
    if not group or str(group.leaders.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Xóa task khỏi nhóm
    if group.allTasks:
        group.allTasks = [t for t in group.allTasks if str(t.id) != task_id]
        await group.save()

    # Xóa task khỏi sinh viên
    students = await task.assigned_students.fetch() if task.assigned_students else []
    for student in students:
        if student.tasks:
            student.tasks = [t for t in student.tasks if str(t.id) != task_id]
            await student.save()

    await task.delete()
    return {"message": "Task deleted"}
