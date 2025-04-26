from fastapi import APIRouter, Depends, HTTPException, status
from models.group_model import Group
from models.project_model import Project
from models.user_model import User
from schemas.group_schemas import GroupCreate, GroupResponse
from routes.user_routes import get_current_admin

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=GroupResponse)
async def create_group(group: GroupCreate, current_user: User = Depends(get_current_admin)):
    project = await Project.get(group.project_id)
    if not project or str(project.mentor.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")

    new_group = Group(
        name=group.name,
        project=project,
        leaders=current_user,
        members=[],
        allTasks=[]
    )
    await new_group.insert()

    # Thêm nhóm vào dự án
    if not project.groups:
        project.groups = []
    project.groups.append(new_group)
    await project.save()
    
    return new_group

@router.get("/{project_id}", response_model=list[GroupResponse])
async def get_groups(project_id: str, current_user: User = Depends(get_current_admin)):
    project = await Project.get(project_id)
    if not project or str(project.mentor.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    groups = await Group.find({"project.$id": project.id}).to_list()
    return groups

@router.post("/{group_id}/add-student/{student_id}")
async def add_student_to_group(group_id: str, student_id: str, current_user: User = Depends(get_current_admin)):
    group = await Group.get(group_id)
    student = await User.get(student_id)
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")
    if str(group.leaders.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    if not group.members:
        group.members = []
    if student not in group.members:
        group.members.append(student)
        student.group_id = group
        await student.save()
        await group.save()
    
    return {"message": "Student added to group"}

@router.delete("/{group_id}")
async def delete_group(group_id: str, current_user: User = Depends(get_current_admin)):
    group = await Group.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if str(group.leaders.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Xóa nhóm khỏi dự án
    project = await group.project.fetch()
    if project.groups:
        project.groups = [g for g in project.groups if str(g.id) != group_id]
        await project.save()

    # Xóa group_id khỏi các sinh viên trong nhóm
    members = await group.members.fetch() if group.members else []
    for student in members:
        student.group_id = None
        await student.save()
    
    # Xóa các task liên quan
    tasks = await group.allTasks.fetch() if group.allTasks else []
    for task in tasks:
        await task.delete()

    await group.delete()
    return {"message": "Group deleted"}