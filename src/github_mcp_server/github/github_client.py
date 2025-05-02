"""
GitHub client implementation for MCP server
"""

from typing import Dict, List, Optional, Any, Union
import github
from github import Github
from github.GithubException import GithubException
from loguru import logger


class GitHubClient:
    """
    GitHub client interface for MCP server
    
    Provides methods to interact with GitHub API using PyGithub library.
    """
    
    def __init__(
        self, 
        personal_access_token: str, 
        host: Optional[str] = None,
        user_agent: str = "github-mcp-server/0.1.0",
        mock_mode: bool = False
    ):
        """
        Initialize the GitHub client
        
        Args:
            personal_access_token: GitHub personal access token
            host: GitHub Enterprise host (optional)
            user_agent: User agent string for API requests
        """
        self.token = personal_access_token
        self.host = host
        self.user_agent = user_agent
        self.mock_mode = mock_mode
        self._client = None
        
        # Initialize GitHub client
        self._init_client()
    
    def _init_client(self) -> None:
        """
        Initialize the GitHub client with the current configuration
        """
        try:
            if self.host:
                # Connect to GitHub Enterprise
                base_url = f"https://{self.host}/api/v3"
                self._client = Github(
                    self.token,
                    base_url=base_url,
                    user_agent=self.user_agent
                )
            else:
                # Connect to GitHub.com
                self._client = Github(
                    self.token,
                    user_agent=self.user_agent
                )
            
            # Test connection by getting authenticated user
            user = self._client.get_user()
            logger.debug(f"GitHub client initialized for user: {user.login}")
        except GithubException as e:
            logger.error(f"Failed to initialize GitHub client: {e}")
            raise
    
    @property
    def client(self) -> Github:
        """
        Get the PyGithub client instance
        """
        if not self._client:
            self._init_client()
        return self._client
    
    def set_user_agent(self, user_agent: str) -> None:
        """
        Update the user agent string
        """
        self.user_agent = user_agent
        # Recreate client with new user agent
        self._init_client()
    
    # User operations
    def get_authenticated_user(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user
        """
        try:
            user = self.client.get_user()
            return {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "html_url": user.html_url,
                "id": user.id,
                "type": user.type
            }
        except GithubException as e:
            logger.error(f"Failed to get authenticated user: {e}")
            raise
    
    # Repository operations
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            return {
                "name": repository.name,
                "full_name": repository.full_name,
                "description": repository.description,
                "html_url": repository.html_url,
                "default_branch": repository.default_branch,
                "owner": {
                    "login": repository.owner.login,
                    "id": repository.owner.id,
                    "type": repository.owner.type,
                    "avatar_url": repository.owner.avatar_url
                },
                "is_private": repository.private,
                "is_fork": repository.fork,
                "created_at": repository.created_at.isoformat(),
                "updated_at": repository.updated_at.isoformat(),
                "pushed_at": repository.pushed_at.isoformat()
            }
        except GithubException as e:
            logger.error(f"Failed to get repository {owner}/{repo}: {e}")
            raise
    
    def get_repositories(
        self, 
        visibility: str = "all", 
        sort: str = "updated", 
        direction: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Get repositories for authenticated user
        """
        try:
            repos = []
            for repo in self.client.get_user().get_repos(
                visibility=visibility, 
                sort=sort, 
                direction=direction
            ):
                repos.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "html_url": repo.html_url,
                    "default_branch": repo.default_branch,
                    "owner": {
                        "login": repo.owner.login,
                        "id": repo.owner.id,
                        "type": repo.owner.type,
                        "avatar_url": repo.owner.avatar_url
                    },
                    "is_private": repo.private,
                    "is_fork": repo.fork
                })
            return repos
        except GithubException as e:
            logger.error(f"Failed to get repositories: {e}")
            raise
    
    # Branch operations
    def get_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        Get branches for a repository
        """
        try:
            branches = []
            repository = self.client.get_repo(f"{owner}/{repo}")
            for branch in repository.get_branches():
                branches.append({
                    "name": branch.name,
                    "commit": {
                        "sha": branch.commit.sha,
                        "url": branch.commit.url
                    },
                    "protected": branch.protected
                })
            return branches
        except GithubException as e:
            logger.error(f"Failed to get branches for {owner}/{repo}: {e}")
            raise
    
    # Issue operations
    def get_issues(
        self, 
        owner: str, 
        repo: str, 
        state: str = "open", 
        sort: str = "created", 
        direction: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Get issues for a repository
        """
        try:
            issues = []
            repository = self.client.get_repo(f"{owner}/{repo}")
            for issue in repository.get_issues(state=state, sort=sort, direction=direction):
                issues.append({
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "html_url": issue.html_url,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "user": {
                        "login": issue.user.login,
                        "id": issue.user.id,
                        "avatar_url": issue.user.avatar_url
                    }
                })
            return issues
        except GithubException as e:
            logger.error(f"Failed to get issues for {owner}/{repo}: {e}")
            raise
    
    def create_issue(
        self, 
        owner: str, 
        repo: str, 
        title: str, 
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue in a repository
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issue = repository.create_issue(
                title=title,
                body=body,
                labels=labels,
                assignees=assignees
            )
            return {
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "html_url": issue.html_url,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "user": {
                    "login": issue.user.login,
                    "id": issue.user.id,
                    "avatar_url": issue.user.avatar_url
                }
            }
        except GithubException as e:
            logger.error(f"Failed to create issue in {owner}/{repo}: {e}")
            raise
    
    # Pull request operations
    def get_pull_requests(
        self, 
        owner: str, 
        repo: str, 
        state: str = "open", 
        sort: str = "created", 
        direction: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Get pull requests for a repository
        """
        try:
            pull_requests = []
            repository = self.client.get_repo(f"{owner}/{repo}")
            for pr in repository.get_pulls(state=state, sort=sort, direction=direction):
                pull_requests.append({
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "html_url": pr.html_url,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat(),
                    "user": {
                        "login": pr.user.login,
                        "id": pr.user.id,
                        "avatar_url": pr.user.avatar_url
                    },
                    "merged": pr.merged,
                    "mergeable": pr.mergeable,
                    "base": {
                        "ref": pr.base.ref,
                        "label": pr.base.label
                    },
                    "head": {
                        "ref": pr.head.ref,
                        "label": pr.head.label
                    }
                })
            return pull_requests
        except GithubException as e:
            logger.error(f"Failed to get pull requests for {owner}/{repo}: {e}")
            raise
    
    # Content operations
    def get_file_content(
        self, 
        owner: str, 
        repo: str, 
        path: str, 
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get file content from a repository
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            content = repository.get_contents(path, ref=ref)
            
            if isinstance(content, List):
                # Directory content
                contents = []
                for item in content:
                    contents.append({
                        "name": item.name,
                        "path": item.path,
                        "type": item.type,
                        "sha": item.sha,
                        "download_url": item.download_url
                    })
                return {
                    "type": "directory",
                    "contents": contents
                }
            else:
                # File content
                return {
                    "type": "file",
                    "name": content.name,
                    "path": content.path,
                    "sha": content.sha,
                    "encoding": content.encoding,
                    "content": content.decoded_content.decode("utf-8"),
                    "download_url": content.download_url
                }
        except GithubException as e:
            logger.error(f"Failed to get content for {path} in {owner}/{repo}: {e}")
            raise
