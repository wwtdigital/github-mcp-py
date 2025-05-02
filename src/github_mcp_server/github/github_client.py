"""
GitHub client implementation for MCP server
"""

from typing import Dict, List, Optional, Any, Union
import os
from github import Github
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.GithubException import GithubException
from loguru import logger

from ..config import Config
from .graphql_client import GitHubGraphQLClient

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
            mock_mode: Whether to run in mock mode without a real token
        """
        self.token = personal_access_token
        self.host = host
        self.user_agent = user_agent
        self.mock_mode = mock_mode
        self._client = None
        self._graphql_client = None
        
        # Initialize GitHub clients
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
            
            # Initialize GraphQL client using a configuration object that matches what the client expects
            config = Config()
            config.github_personal_access_token = self.token
            config.github_host = self.host
            config.github_read_only = False  # This will be handled at the toolset level
            
            self._graphql_client = GitHubGraphQLClient(config)
            
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
    
    @property
    def graphql_client(self) -> GitHubGraphQLClient:
        """
        Get the GraphQL client instance
        """
        if not self._graphql_client:
            self._init_client()
        return self._graphql_client
    
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
        Get projects for a repository using GraphQL API
        
        The REST API for classic Projects is deprecated, so we use GraphQL instead.
        """
        try:
            # Use GraphQL client to get repository projects
            result = self.graphql_client.list_repository_projects(owner, repo)
            
            # Extract projects from the result
            projects = []
            if result.get('repository', {}).get('projectsV2', {}).get('nodes'):
                for project in result['repository']['projectsV2']['nodes']:
                    projects.append({
                        "id": project.get('id'),
                        "name": project.get('title'),
                        "number": project.get('number'),
                        "body": project.get('shortDescription'),
                        "state": 'open' if not project.get('closed') else 'closed',
                        "html_url": project.get('url'),
                        "created_at": project.get('createdAt'),
                        "updated_at": project.get('updatedAt')
                    })
            return projects
        except Exception as e:
            logger.error(f"Failed to get projects for {owner}/{repo}: {e}")
            raise
    
    def get_project_columns(self, owner: str, repo: str, project_number: int) -> List[Dict[str, Any]]:
        """
        Get columns for a project using GraphQL API
        
        In the new Projects v2, the concept of "columns" is replaced by "fields",
        specifically a single select field that indicates the status.
        """
        try:
            # First get the project ID using GraphQL
            result = self.graphql_client.list_repository_projects(owner, repo)
            
            project_id = None
            if result.get('repository', {}).get('projectsV2', {}).get('nodes'):
                for project in result['repository']['projectsV2']['nodes']:
                    if project.get('number') == project_number:
                        project_id = project.get('id')
                        break
                        
            if not project_id:
                raise ValueError(f"Project {project_number} not found in {owner}/{repo}")
                
            # Get project fields
            fields_result = self.graphql_client.get_project_fields(project_id)
            
            # Extract status fields (single select fields)
            columns = []
            if fields_result.get('node', {}).get('fields', {}).get('nodes'):
                for field in fields_result['node']['fields']['nodes']:
                    # Only include single select fields, which are like columns in the old projects
                    if 'options' in field:
                        for option in field.get('options', []):
                            columns.append({
                                "id": option.get('id'),
                                "name": option.get('name'),
                                "created_at": None,  # Not available in GraphQL API
                                "updated_at": None,  # Not available in GraphQL API
                                "color": option.get('color')
                            })
                
            return columns
        except Exception as e:
            logger.error(f"Failed to get columns for project {project_number} in {owner}/{repo}: {e}")
            raise
    
    def get_project_cards(self, owner: str, repo: str, project_number: int, status_name: str) -> List[Dict[str, Any]]:
        """
        Get cards (items) for a project with a specific status
        
        In the new Projects v2, items can have various fields, and one of these is typically
        a status field that represents what was previously a column in classic Projects.
        
        Args:
            owner: Repository owner
            repo: Repository name
            project_number: Project number
            status_name: Status name (like 'To Do', 'In Progress', 'Done')
        """
        try:
            # First get the project ID using GraphQL
            result = self.graphql_client.list_repository_projects(owner, repo)
            
            project_id = None
            project_title = None
            if result.get('repository', {}).get('projectsV2', {}).get('nodes'):
                for project in result['repository']['projectsV2']['nodes']:
                    if project.get('number') == project_number:
                        project_id = project.get('id')
                        project_title = project.get('title')
                        break
                        
            if not project_id:
                raise ValueError(f"Project {project_number} not found in {owner}/{repo}")
            
            # Get all items in the project
            items_result = self.graphql_client.get_project_items(project_id)
            
            # Extract items that match the specified status
            cards = []
            if items_result.get('node', {}).get('items', {}).get('nodes'):
                for item in items_result['node']['items']['nodes']:
                    # Check if this item has the requested status
                    status_field_value = None
                    
                    # Go through field values to find status fields
                    if item.get('fieldValues', {}).get('nodes'):
                        for field_value in item['fieldValues']['nodes']:
                            # Look for the status field
                            if field_value.get('field', {}).get('name') == 'Status' and field_value.get('name') == status_name:
                                status_field_value = field_value.get('name')
                                break
                    
                    # Only include items that have the requested status
                    if status_field_value == status_name:
                        # Get issue or PR data if content exists
                        issue_data = None
                        pr_data = None
                        
                        if item.get('content'):
                            content = item['content']
                            if 'Issue' in content.get('__typename', ''):
                                issue_data = {
                                    "number": content.get('number'),
                                    "title": content.get('title'),
                                    "state": content.get('state'),
                                    "html_url": f"https://github.com/{owner}/{repo}/issues/{content.get('number')}"
                                }
                            elif 'PullRequest' in content.get('__typename', ''):
                                pr_data = {
                                    "number": content.get('number'),
                                    "title": content.get('title'),
                                    "state": content.get('state'),
                                    "html_url": f"https://github.com/{owner}/{repo}/pull/{content.get('number')}"
                                }
                        
                        cards.append({
                            "id": item.get('id'),
                            "note": None,  # Note is not available in Projects v2
                            "created_at": None,  # Not directly available
                            "updated_at": None,  # Not directly available
                            "issue": issue_data,
                            "pull_request": pr_data,
                            "status": status_name
                        })
                
            return cards
        except Exception as e:
            logger.error(f"Failed to get cards with status '{status_name}' in project {project_number}: {e}")
            raise
    
    def move_project_card(self, owner: str, repo: str, project_number: int, 
                       item_id: str, status_value: str, position: str = "top"):
        """
        Update an item's status in a project
        
        In Projects v2, instead of moving cards between columns, you update a status field.
        
        Args:
            owner: Repository owner
            repo: Repository name
            project_number: Project number
            item_id: Node ID of the project item
            status_value: Status value to set
            position: Position (not used in Projects v2, kept for API compatibility)
        """
        try:
            # First get the project ID using GraphQL
            result = self.graphql_client.list_repository_projects(owner, repo)
            
            project_id = None
            if result.get('repository', {}).get('projectsV2', {}).get('nodes'):
                for project in result['repository']['projectsV2']['nodes']:
                    if project.get('number') == project_number:
                        project_id = project.get('id')
                        break
                        
            if not project_id:
                raise ValueError(f"Project {project_number} not found in {owner}/{repo}")
                
            # Get project fields to find the status field
            fields_result = self.graphql_client.get_project_fields(project_id)
            
            status_field_id = None
            status_options = {}
            
            if fields_result.get('node', {}).get('fields', {}).get('nodes'):
                for field in fields_result['node']['fields']['nodes']:
                    # Look for single select fields which are likely status fields
                    if 'options' in field:
                        # Typically the Status field would be named 'Status'
                        if field.get('name') == 'Status':
                            status_field_id = field.get('id')
                            # Map option names to IDs
                            for option in field.get('options', []):
                                status_options[option.get('name')] = option.get('id')
                            break
            
            if not status_field_id:
                raise ValueError(f"Status field not found in project {project_number}")
                
            # Check if the requested status value exists
            if status_value not in status_options:
                raise ValueError(f"Status '{status_value}' not found in project {project_number}. Available statuses: {list(status_options.keys())}")
                
            # Update the item's status field
            # In GraphQL, we need to provide a JSON-formatted string for single select fields
            value = {"singleSelectOptionId": status_options[status_value]}
            
            result = self.graphql_client.update_project_item_field(
                project_id=project_id,
                item_id=item_id,
                field_id=status_field_id,
                value=value
            )
            
            # Return success response
            return {
                "success": True,
                "item_id": item_id,
                "status": status_value,
                "project_number": project_number
            }
        except Exception as e:
            logger.error(f"Failed to update status to '{status_value}' for item {item_id}: {e}")
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
