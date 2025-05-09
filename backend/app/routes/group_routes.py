from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.group_model import Group
from models.project_model import Project
from models.user_model import User
from models.task_model import Task
from schemas.group_schemas import GroupCreate, GroupResponse, PyObjectId
from routes.user_routes import get_current_mentor
from beanie import Link
import asyncio
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
        group.project_id = PyObjectId.validate(group.project_id)
        project = await Project.get(group.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch mentor từ project để kiểm tra
        # mentor = await project.mentor.fetch()
        if not current_user:
            logger.error(f"Mentor not found for project {project.id}")
            raise HTTPException(status_code=404, detail="Mentor associated with project not found")

        if str(current_user.id) != str(current_user.id):
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
            project_title=project.title,
            project_image=project.image,
            project_description=project.description,
            leader_id=str(leader.id),
            leader_email=leader.email,
            leader_name=leader.ho_ten,
            member_ids=[str(member.id) for member in new_group.members],
            member_names=[str(member.ho_ten) for member in new_group.members],
            member_emails=[str(member.email) for member in new_group.members],
        )
   
   
   
    except Exception as e:
        logger.error(f"Error creating group: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/project/{project_id}", response_model=List[dict])
async def get_groups_by_project_id(project_id: str, current_user: User = Depends(get_current_mentor)):
    try:
        # Validate the project_id format
        logger.info(f"Project ID: {project_id}")
        project_id_obj = PyObjectId.validate(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")
    try:
        logger.info(f"Project ID Object: {project_id_obj}")
        # Fetch the project from the database
        project = await Project.get(project_id_obj)
        logger.info(f"Project: {project}")
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Check if the current user is the mentor of the project
        mentor_id = None
        if isinstance(project.mentor, Link):
            mentor = await project.mentor.fetch()
            mentor_id = str(mentor.id) if mentor else None
        elif isinstance(project.mentor, User):
            mentor_id = str(project.mentor.id)
        if mentor_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Fetch all groups associated with the project
        logger.info(f"Fetching groups for project ID: {project_id_obj}")
        groups = await Group.find({"project.$id": project_id_obj}).to_list()
        logger.info(f"Groups found: {groups}")

        # Prepare the response
        result = []
        for group in groups:
            # Fetch leader
            leader = await group.leaders.fetch() if isinstance(group.leaders, Link) else group.leaders
            if not leader:
                logger.warning(f"Failed to fetch leader for group {group.id}")
                continue

           

            result.append({
                "id": str(group.id),
                "name": group.name,
                "project_id": str(project.id),
                "project_title": project.title,
                "project_image": project.image,
                "project_description": project.description,
                "leader_name": leader.ho_ten if leader else None,
                "leader_id": str(leader.id) if leader else None,
                "leader_email": leader.email if leader else None,
                
            })

        return result
    except Exception as e:
        logger.error(f"Error fetching groups for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{group_id}/add-member/{member_id}", response_model=bool)
async def add_member_to_group(group_id: str, member_id: str, current_user: User = Depends(get_current_mentor)):

    try:
        # Validate group_id and member_id
        group_id_obj = PyObjectId.validate(group_id)
        member_id_obj = PyObjectId.validate(member_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group_id or member_id format")

    try:
        # Fetch the group from the database
        group = await Group.get(group_id_obj)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")


        member = await User.get(member_id_obj)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Check if the member is already in the group
        if member in group.members:
            raise HTTPException(status_code=400, detail="Member is already in the group")

        # Add the member to the group
        group.members.append(Link(member, document_class=User))
        await group.save()

        logger.info(f"Added member {member.id} to group {group.id}")

        return True
    except Exception as e:
        logger.error(f"Error adding member {member_id} to group {group_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{group_id}/change-leader/{new_leader_id}", response_model=dict)
async def change_group_leader(group_id: str, new_leader_id: str, current_user: User = Depends(get_current_mentor)):
    """
    Change the leader of a group.
    """
    try:
        # Validate group_id and new_leader_id
        group_id_obj = PyObjectId.validate(group_id)
        new_leader_id_obj = PyObjectId.validate(new_leader_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group_id or new_leader_id format")

    try:
        # Fetch the group from the database
        group = await Group.get(group_id_obj)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        members = await asyncio.gather(*[member.fetch() for member in group.members])
        # Fetch the new leader from the database
        new_leader = await User.get(new_leader_id_obj)
        print(f"New leader: {new_leader}")
        if not new_leader:
            raise HTTPException(status_code=404, detail="New leader not found")

        # Ensure the new leader is a student
        if new_leader.role != "student":
            raise HTTPException(status_code=400, detail="New leader must be a student")

        # Ensure the new leader is a member of the group
        member_ids = [member.id for member in members]
        if new_leader_id_obj not in member_ids:
            raise HTTPException(status_code=400, detail="New leader is not a member of the group")
        # Update the leader of the group
        group.leaders = Link(new_leader, document_class=User)
        await group.save()

        logger.info(f"Changed leader of group {group.id} to {new_leader.id}")
        # Prepare the response
        return {
            "message": "Leader changed successfully",
            "new_leader_id": str(new_leader.id),
            "new_leader_name": new_leader.ho_ten,
            "group_name": group.name,
            "group_id": str(group.id)
        }
    except Exception as e:
        logger.error(f"Error changing leader of group {group_id} to {new_leader_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{group_id}/remove-member/{member_id}", response_model=dict)
async def remove_member_from_group(group_id: str, member_id: str, current_user: User = Depends(get_current_mentor)):
    """
    Remove a member from a group.
    """
    try:
        # Validate group_id and member_id
        group_id_obj = PyObjectId.validate(group_id)
        member_id_obj = PyObjectId.validate(member_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group_id or member_id format")

    try:
        # Fetch the group from the database
        group = await Group.get(group_id_obj)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Fetch the member from the database
        member = await User.get(member_id_obj)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        members = await asyncio.gather(*[member.fetch() for member in group.members])
        # Ensure the member is part of the group
        if member_id_obj not in [m.id for m in members]:
            raise HTTPException(status_code=400, detail="Member is not part of the group")

        # Remove the member from the group
        group.members = [m for m in members if m.id != member_id_obj]
        await group.save()

        # Update the member's group_id to None
        member.group_id = None
        await member.save()

        logger.info(f"Removed member {member.id} from group {group.id}")

        # Prepare the response
        return {
            "message": "Member removed successfully",
            "removed_member_id": str(member.id),
            "group_name": group.name,
            "group_id": str(group.id)
        }
    except Exception as e:
        logger.error(f"Error removing member {member_id} from group {group_id}: {str(e)}")
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