from fastapi import HTTPException
from config import env
from github import Github

class GitHubService:
    def __init__(self):
        self.github = Github(env.GITHUB_TOKEN)
    
    def get_user_repositories(self, username=None):
        """Lấy danh sách repositories của user hoặc người dùng hiện tại"""
        if username:
            user = self.github.get_user(username)
        else:
            user = self.github.get_user()
        
        repos = []
        for repo in user.get_repos():
            repos.append({
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "language": repo.language,
                "stars": repo.stargazers_count
            })
        return repos
    
    def get_repo_commits(self, repo_name, username=None):
        """Lấy danh sách commits của repository"""
        if username:
            repo = self.github.get_repo(f"{username}/{repo_name}")
        else:
            user = self.github.get_user()
            repo = self.github.get_repo(f"{user.login}/{repo_name}")
        
        commits = []
        for commit in repo.get_commits():
            commits.append({
                "sha": commit.sha,
                "message": commit.commit.message,
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat()
            })
        return commits
    
    def get_repo_contributors(self, repo_name, username=None):
        """Lấy danh sách contributors của repository"""
        if username:
            repo = self.github.get_repo(f"{username}/{repo_name}")
        else:
            user = self.github.get_user()
            repo = self.github.get_repo(f"{user.login}/{repo_name}")
        
        contributors = []
        for contributor in repo.get_contributors():
            contributors.append({
                "login": contributor.login,
                "contributions": contributor.contributions,
                "avatar_url": contributor.avatar_url,
                "profile_url": contributor.html_url
            })
        return contributors
    
    def analyze_contributor_activity(self, repo_name, username=None):
        """Phân tích hoạt động của các contributors"""
        try:
            if username:
                repo = self.github.get_repo(f"{username}/{repo_name}")
            else:
                user = self.github.get_user()
                repo = self.github.get_repo(f"{user.login}/{repo_name}")
            
            contributors = {}
            commits = repo.get_commits()
            
            for commit in commits:
                author = commit.commit.author.name
                if not author:
                    continue

                if author not in contributors:
                    contributors[author] = {
                        "commit_count": 0,
                        "lines_added": 0,
                        "lines_removed": 0,
                        "files_modified": 0,
                        "last_commit_date": None
                    }
                
                contributors[author]["commit_count"] += 1
                contributors[author]["last_commit_date"] = commit.commit.author.date

                try:
                    full_commit = repo.get_commit(commit.sha)
                    contributors[author]["lines_added"] += full_commit.stats.additions
                    contributors[author]["lines_removed"] += full_commit.stats.deletions
                    contributors[author]["files_modified"] += len(full_commit.files)
                except Exception:
                    continue

            return contributors
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error analyzing repository: {str(e)}")

