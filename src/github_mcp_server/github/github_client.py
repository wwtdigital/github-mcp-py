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
    
    # Project methods
    def get_projects(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        Get projects for a repository
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            projects = []
            for project in repository.get_projects():
                projects.append({
                    "id": project.id,
                    "name": project.name,
                    "body": project.body,
                    "number": project.number,
                    "state": project.state,
                    "html_url": project.html_url,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None
                })
            return projects
        except GithubException as e:
            logger.error(f"Failed to get projects for {owner}/{repo}: {e}")
            raise
    
    def get_project_columns(self, owner: str, repo: str, project_number: int) -> List[Dict[str, Any]]:
        """
        Get columns for a project
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            project = None
            
            # Find the project with the specified number
            for proj in repository.get_projects():
                if proj.number == project_number:
                    project = proj
                    break
            
            if project is None:
                raise ValueError(f"Project number {project_number} not found")
            
            columns = []
            for column in project.get_columns():
                columns.append({
                    "id": column.id,
                    "name": column.name,
                    "created_at": column.created_at.isoformat() if column.created_at else None,
                    "updated_at": column.updated_at.isoformat() if column.updated_at else None
                })
            return columns
        except GithubException as e:
            logger.error(f"Failed to get columns for project {project_number} in {owner}/{repo}: {e}")
            raise
    
    def get_project_cards(self, owner: str, repo: str, project_number: int, column_name: str) -> List[Dict[str, Any]]:
        """
        Get cards for a project column
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            project = None
            
            # Find the project with the specified number
            for proj in repository.get_projects():
                if proj.number == project_number:
                    project = proj
                    break
            
            if project is None:
                raise ValueError(f"Project number {project_number} not found")
            
            # Find the column with the specified name
            column = None
            for col in project.get_columns():
                if col.name == column_name:
                    column = col
                    break
            
            if column is None:
                raise ValueError(f"Column {column_name} not found in project {project_number}")
            
            cards = []
            for card in column.get_cards():
                card_data = {
                    "id": card.id,
                    "note": card.note,
                    "created_at": card.created_at.isoformat() if card.created_at else None,
                    "updated_at": card.updated_at.isoformat() if card.updated_at else None,
                }
                
                # If the card is associated with an issue or PR, include that info
                if card.content_url:
                    try:
                        # Parse the content URL to determine if it's an issue or PR
                        parts = card.content_url.split('/')
                        if 'issues' in parts or 'pull' in parts:
                            issue_number = int(parts[-1])
                            issue = repository.get_issue(issue_number)
                            card_data["content_type"] = "Issue" if issue.pull_request is None else "PullRequest"
                            card_data["content"] = {
                                "number": issue.number,
                                "title": issue.title,
                                "html_url": issue.html_url
                            }
                    except Exception as e:
                        logger.warning(f"Could not fetch content for card {card.id}: {e}")
                
                cards.append(card_data)
            
            return cards
        except GithubException as e:
            logger.error(f"Failed to get cards for column {column_name} in project {project_number} in {owner}/{repo}: {e}")
            raise
    
    def move_project_card(self, owner: str, repo: str, project_number: int, 
                       card_id: int, target_column: str, position: str = "top") -> Dict[str, Any]:
        """
        Move a card to a different column in a project
        
        Args:
            owner: Repository owner
            repo: Repository name
            project_number: Project number
            card_id: ID of the card to move
            target_column: Name of the destination column
            position: Card position (top, bottom, or after:<card-id>)
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            project = None
            
            # Find the project with the specified number
            for proj in repository.get_projects():
                if proj.number == project_number:
                    project = proj
                    break
            
            if project is None:
                raise ValueError(f"Project number {project_number} not found")
            
            # Find the target column with the specified name
            target_col = None
            for col in project.get_columns():
                if col.name == target_column:
                    target_col = col
                    break
            
            if target_col is None:
                raise ValueError(f"Column {target_column} not found in project {project_number}")
            
            # Find the card
            card = None
            for col in project.get_columns():
                for c in col.get_cards():
                    if c.id == card_id:
                        card = c
                        break
                if card:
                    break
            
            if card is None:
                raise ValueError(f"Card with ID {card_id} not found in project {project_number}")
            
            # Move the card to the target column
            result = card.move(position, target_col.id)
            
            return {
                "success": True,
                "card_id": card_id,
                "target_column": target_column,
                "position": position
            }
        except GithubException as e:
            logger.error(f"Failed to move card {card_id} to {target_column} in project {project_number}: {e}")
            raise
    
    # Issue label methods
    def get_labels(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        Get labels for a repository
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            labels = []
            for label in repository.get_labels():
                labels.append({
                    "name": label.name,
                    "color": label.color,
                    "description": label.description,
                    "url": label.url
                })
            return labels
        except GithubException as e:
            logger.error(f"Failed to get labels for {owner}/{repo}: {e}")
            raise
    
    def add_issue_labels(self, owner: str, repo: str, issue_number: int, labels: List[str]) -> List[Dict[str, Any]]:
        """
        Add labels to an issue
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(issue_number)
            added_labels = issue.add_to_labels(*labels)
            
            result = []
            for label in added_labels:
                result.append({
                    "name": label.name,
                    "color": label.color,
                    "description": label.description,
                    "url": label.url
                })
            return result
        except GithubException as e:
            logger.error(f"Failed to add labels to issue {issue_number} in {owner}/{repo}: {e}")
            raise
    
    def remove_issue_label(self, owner: str, repo: str, issue_number: int, label: str) -> bool:
        """
        Remove a label from an issue
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(issue_number)
            issue.remove_from_labels(label)
            return True
        except GithubException as e:
            logger.error(f"Failed to remove label {label} from issue {issue_number} in {owner}/{repo}: {e}")
            raise
    
    # Issue comment methods
    def get_issue_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]:
        """
        Get comments for an issue
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(issue_number)
            comments = []
            for comment in issue.get_comments():
                comments.append({
                    "id": comment.id,
                    "body": comment.body,
                    "created_at": comment.created_at.isoformat() if comment.created_at else None,
                    "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
                    "user": {
                        "login": comment.user.login,
                        "id": comment.user.id,
                        "avatar_url": comment.user.avatar_url
                    }
                })
            return comments
        except GithubException as e:
            logger.error(f"Failed to get comments for issue {issue_number} in {owner}/{repo}: {e}")
            raise
    
    def add_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
        """
        Add a comment to an issue
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(issue_number)
            comment = issue.create_comment(body)
            
            return {
                "id": comment.id,
                "body": comment.body,
                "created_at": comment.created_at.isoformat() if comment.created_at else None,
                "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
                "user": {
                    "login": comment.user.login,
                    "id": comment.user.id,
                    "avatar_url": comment.user.avatar_url
                }
            }
        except GithubException as e:
            logger.error(f"Failed to add comment to issue {issue_number} in {owner}/{repo}: {e}")
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
