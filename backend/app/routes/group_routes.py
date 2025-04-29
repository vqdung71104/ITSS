from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.group_model import Group
from models.project_model import Project
from models.user_model import User
from models.task_model import Task
from schemas.group_schemas import GroupCreate, GroupResponse, GroupListResponse, PyObjectId
from routes.user_routes import get_current_mentor
from beanie import Link
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=GroupResponse)
async def create_group(group: GroupCreate, current_user: User = Depends(get_current_mentor)):
    try:
        project = await Project.get(group.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch mentor từ project để kiểm tra
        mentor = await project.mentor.fetch()
        if not mentor:
            logger.error(f"Mentor not found for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Lấy leader từ leader_id
        leader_id_obj = PyObjectId.validate(group.leader_id)
        leader = await User.get(leader_id_obj)
        if not leader:
            raise HTTPException(status_code=404, detail="Leader not found")
        if leader.role != "student":
            raise HTTPException(status_code=400, detail="Leader must be a student")

        new_group = Group(
            name=group.name,
            project=Link(project, document_class=Project),
            leaders=Link(leader, document_class=User),
            members=[],
            tasks=[],
            allTasks=[]
        )
        await new_group.insert()

        logger.info(f"Created new group: {new_group.id}")

        return GroupResponse(
            id=str(new_group.id),
            name=new_group.name,
            project_id=str(project.id),
            leader_id=str(leader.id),
            member_ids=[],
            task_ids=[]
        )
    except Exception as e:
        logger.error(f"Error creating group: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{project_id}", response_model=List[GroupListResponse])
async def get_groups(project_id: str, current_user: User = Depends(get_current_mentor)):
    try:
        project_id_obj = PyObjectId.validate(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")

    try:
        project = await Project.get(project_id_obj)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch mentor từ project để kiểm tra
        mentor = await project.mentor.fetch()
        if not mentor:
            logger.error(f"Mentor not found for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        groups = await Group.find({"project.$id": project.id}).to_list()

        group_responses = []
        for group in groups:
            members = await group.fetch_link("members") or []
            tasks = await group.fetch_link("allTasks") or []

            # Chỉ lấy leader_id từ Link, không fetch nếu không cần thiết
            if not group.leaders.ref or not group.leaders.ref.id:
                logger.error(f"Invalid leaders reference for group {group.id}")
                continue
            leader_id = str(group.leaders.ref.id)

            group_responses.append(GroupListResponse(
                id=str(group.id),
                name=group.name,
                project_id=str(group.project.ref.id),
                leader_id=leader_id,
                member_ids=[str(member.id) for member in members] if members else [],
                task_ids=[str(task.id) for task in tasks] if tasks else []
            ))

        return group_responses
    except Exception as e:
        logger.error(f"Error getting groups: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{group_id}/add-member/{member_id}", response_model=dict)
async def add_member_to_group(group_id: str, member_id: str, current_user: User = Depends(get_current_mentor)):
    try:
        group_id_obj = PyObjectId.validate(group_id)
        member_id_obj = PyObjectId.validate(member_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    try:
        logger.info(f"Attempting to add member {member_id} to group {group_id}")

        # Lấy group và member với await
        group = await Group.get(group_id_obj)
        logger.info(f"Retrieved group: {group}")
        member = await User.get(member_id_obj)
        logger.info(f"Retrieved member: {member}")

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        if member.role != "student":
            raise HTTPException(status_code=400, detail="Member must be a student")

        # Fetch project để kiểm tra quyền
        project = await group.project.fetch()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch mentor từ project để kiểm tra
        mentor = await project.mentor.fetch()
        if not mentor:
            logger.error(f"Mentor not found for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Check if member already in group
        members = await group.fetch_link("members") or []
        if any(str(m.id) == member_id for m in members):
            return {"message": "Member already in group"}

        # Add member to group
        member_link = Link(member, document_class=User)
        logger.info(f"Attempting to update group {group.id} with member link: {member_link}")
        
        
        await Group.find_one({"_id": group.id}).update({"$push": {"members": member_link}})
        logger.info(f"Successfully updated group {group.id}")

        # Update member's group reference
        group_link = Link(group, document_class=Group)
        logger.info(f"Attempting to update user {member.id} with group link: {group_link}")
        
        #await User.get() trước khi update
        await User.find_one({"_id": member.id}).update({"$set": {"group_id": group_link}})
        logger.info(f"Successfully updated user {member.id}")

        logger.info(f"Added member {member_id} to group {group_id}")

        return {"message": "Member added to group"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error adding member to group: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{group_id}/change-leader/{new_leader_id}", response_model=GroupResponse)
async def change_leader(group_id: str, new_leader_id: str, current_user: User = Depends(get_current_mentor)):
    try:
        group_id_obj = PyObjectId.validate(group_id)
        new_leader_id_obj = PyObjectId.validate(new_leader_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    try:
        group = await Group.get(group_id_obj)
        new_leader = await User.get(new_leader_id_obj)

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if not new_leader:
            raise HTTPException(status_code=404, detail="New leader not found")
        if new_leader.role != "student":
            raise HTTPException(status_code=400, detail="New leader must be a student")

        # Fetch project để kiểm tra quyền
        project = await group.project.fetch()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch mentor từ project để kiểm tra
        mentor = await project.mentor.fetch()
        if not mentor:
            logger.error(f"Mentor not found for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Fetch leader hiện tại để kiểm tra
        old_leader = await group.leaders.fetch()
        if not old_leader:
            raise HTTPException(status_code=404, detail="Current leader not found")
        if old_leader.role != "student":
            raise HTTPException(status_code=400, detail="Current leader must be a student")

        # Kiểm tra new_leader có trong members không
        members = await group.fetch_link("members") or []
        if not any(str(m.id) == new_leader_id for m in members):
            raise HTTPException(status_code=400, detail="New leader must be a member of the group")

        # Chuyển leader cũ thành member
        group.members = [m for m in members if str(m.id) != new_leader_id]
        group.members.append(Link(old_leader, document_class=User))

        # Gán leader mới
        group.leaders = Link(new_leader, document_class=User)
        await group.save()  # Removed fetch_links=False

        # Cập nhật group_id của old_leader và new_leader
        old_leader.group_id = Link(group, document_class=Group)
        new_leader.group_id = Link(group, document_class=Group)
        await old_leader.save()  # Removed fetch_links=False
        await new_leader.save()  # Removed fetch_links=False

        # Lấy thông tin để trả về
        members = await group.fetch_link("members") or []
        tasks = await group.fetch_link("allTasks") or []

        logger.info(f"Changed leader for group {group.id} to {new_leader.id}")

        return GroupResponse(
            id=str(group.id),
            name=group.name,
            project_id=str(group.project.ref.id),
            leader_id=str(group.leaders.ref.id),
            member_ids=[str(member.id) for member in members] if members else [],
            task_ids=[str(task.id) for task in tasks] if tasks else []
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error changing group leader: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{group_id}/remove-member/{member_id}", response_model=dict)
async def remove_member_from_group(group_id: str, member_id: str, current_user: User = Depends(get_current_mentor)):
    try:
        group_id_obj = PyObjectId.validate(group_id)
        member_id_obj = PyObjectId.validate(member_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    try:
        group = await Group.get(group_id_obj)
        member = await User.get(member_id_obj)

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Fetch project để kiểm tra quyền
        project = await group.project.fetch()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch mentor từ project để kiểm tra
        mentor = await project.mentor.fetch()
        if not mentor:
            logger.error(f"Mentor not found for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Check if member is in group
        members = await group.fetch_link("members") or []
        if not any(str(m.id) == member_id for m in members):
            raise HTTPException(status_code=404, detail="Member not found in group")

        # Remove member from group
        group.members = [m for m in members if str(m.id) != member_id]
        await group.save()  # Removed fetch_links=False

        # Update member's group reference
        member.group_id = None
        await member.save()  # Removed fetch_links=False

        logger.info(f"Removed member {member_id} from group {group_id}")

        return {"message": "Member removed from group"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error removing member from group: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{group_id}")
async def delete_group(group_id: str, current_user: User = Depends(get_current_mentor)):
    try:
        group_id_obj = PyObjectId.validate(group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group_id format")

    try:
        group = await Group.get(group_id_obj)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Fetch project để kiểm tra quyền
        project = await group.project.fetch()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch mentor từ project để kiểm tra
        mentor = await project.mentor.fetch()
        if not mentor:
            logger.error(f"Mentor not found for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(mentor.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Delete all tasks in the group
        tasks = await group.fetch_link("allTasks") or []
        for task in tasks:
            await task.delete()

        # Remove group reference from members
        members = await group.fetch_link("members") or []
        for member in members:
            member.group_id = None
            await member.save()  # Removed fetch_links=False

        # Delete the group
        await group.delete()

        logger.info(f"Deleted group: {group_id}")

        return {"message": "Group deleted"}
    except Exception as e:
        logger.error(f"Error deleting group: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")