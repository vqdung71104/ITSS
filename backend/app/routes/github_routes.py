from fastapi import APIRouter, Depends, HTTPException
from service.github_service import GitHubService
from typing import Optional

router = APIRouter(
    prefix='/github',
    tags=["github"],
    responses={404: {"description": "Not found"}}
)

def get_github_service():
    return GitHubService()

@router.get("/user_github")
async def get_info_user(
    username: str,
    github_service: GitHubService = Depends(get_github_service)
):
    try:
        return github_service.get_user_info(username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

@router.get("/repos")
async def get_repo(
    username: str,
    repo_name: Optional[str] = None,
    type: Optional[str] = None,
    github_service: GitHubService = Depends(get_github_service)
):
    """Lấy thông tin về một kho lưu trữ GitHub"""
    try:
        if type in {"commits", "contributors", "analysis"} and not repo_name:
            raise HTTPException(status_code=400, detail="Missing repo_name for the requested type")

        if type == "commits":
            return github_service.get_repo_commits(repo_name, username)
        elif type == "contributors":
            return github_service.get_repo_contributors(repo_name, username)
        elif type == "analysis":
            return github_service.analyze_contributor_activity(repo_name, username)
        elif type is None:
            return github_service.get_user_repositories(username)
        else:
            raise HTTPException(status_code=400, detail="Invalid type")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_free_rider")
async def get_free_rider(
    username: str,
    repo_name: str,
    github_service: GitHubService = Depends(get_github_service)
):
    try:
        contributors = github_service.analyze_contributor_activity(repo_name, username)
        return contributors
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))