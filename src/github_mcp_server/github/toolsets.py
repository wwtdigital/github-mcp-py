"""
GitHub toolsets for MCP server
"""

from typing import List, Dict, Any, Optional, Callable
from loguru import logger

from github_mcp_server.models import Tool, Resource, Toolset
from github_mcp_server.github.github_client import GitHubClient


# Default tool sets
DEFAULT_TOOLS = ["all"]

# Available toolsets
TOOLSETS = {
    "all": "All available tools",
    "repository": "Repository management tools",
    "issue": "Issue management tools",
    "pullrequest": "Pull request management tools",
    "user": "User management tools",
    "content": "Content management tools",
    "projects": "Project management tools",
    "context": "Context tools",
}


class GithubToolset:
    """
    Base class for GitHub toolsets
    """
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        github_client: GitHubClient,
        read_only: bool = False
    ):
        """
        Initialize a GitHub toolset
        """
        self.name = name
        self.description = description
        self.github_client = github_client
        self.read_only = read_only
        self.tools: List[Tool] = []
        self.resources: List[Resource] = []
    
    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool to the toolset
        """
        self.tools.append(tool)
    
    def add_resource(self, resource: Resource) -> None:
        """
        Add a resource to the toolset
        """
        self.resources.append(resource)
    
    def register_tools(self, server) -> None:
        """
        Register tools with the server
        """
        raise NotImplementedError("Subclasses must implement register_tools")


class RepositoryToolset(GithubToolset):
    """
    Repository management toolset
    """
    
    def __init__(self, github_client: GitHubClient, read_only: bool = False):
        """
        Initialize repository toolset
        """
        super().__init__(
            name="repository",
            description="Repository management tools",
            github_client=github_client,
            read_only=read_only
        )
        
        # Add repository tools
        self.add_tool(Tool(
            name="repository.list",
            description="List repositories for the authenticated user"
        ))
        
        self.add_tool(Tool(
            name="repository.get",
            description="Get repository information"
        ))
        
        self.add_tool(Tool(
            name="repository.branches",
            description="List branches for a repository"
        ))
        
        # Add write operations if not in read-only mode
        if not read_only:
            self.add_tool(Tool(
                name="repository.create",
                description="Create a new repository"
            ))
            
            self.add_tool(Tool(
                name="repository.delete",
                description="Delete a repository"
            ))
    
    def register_tools(self, server) -> None:
        """
        Register repository tools with the server
        """
        # Register repository.list
        async def list_repositories(visibility: str = "all", sort: str = "updated", direction: str = "desc"):
            return self.github_client.get_repositories(
                visibility=visibility,
                sort=sort,
                direction=direction
            )
        server.register_command("repository.list", list_repositories)
        
        # Register repository.get
        async def get_repository(owner: str, repo: str):
            return self.github_client.get_repository(owner, repo)
        server.register_command("repository.get", get_repository)
        
        # Register repository.branches
        async def get_branches(owner: str, repo: str):
            return self.github_client.get_branches(owner, repo)
        server.register_command("repository.branches", get_branches)
        
        # Register write operations if not in read-only mode
        if not self.read_only:
            # These would be implemented in a real server
            pass

class IssueToolset(GithubToolset):
    """
    Issue management toolset
    """
    
    def __init__(self, github_client: GitHubClient, read_only: bool = False):
        """
        Initialize issue toolset
        """
        super().__init__(
            name="issue",
            description="Issue management tools",
            github_client=github_client,
            read_only=read_only
        )
        
        # Add issue tools
        self.add_tool(Tool(
            name="issue.list",
            description="List issues for a repository"
        ))
        
        self.add_tool(Tool(
            name="issue.get",
            description="Get issue information"
        ))
        
        # Add write operations if not in read-only mode
        if not read_only:
            self.add_tool(Tool(
                name="issue.create",
                description="Create a new issue"
            ))
            
            self.add_tool(Tool(
                name="issue.update",
                description="Update an issue"
            ))
            
            self.add_tool(Tool(
                name="issue.close",
                description="Close an issue"
            ))
    
    def register_tools(self, server) -> None:
        """
        Register issue tools with the server
        """
        # Register issue.list
        async def list_issues(owner: str, repo: str, state: str = "open", sort: str = "created", direction: str = "desc"):
            return self.github_client.get_issues(
                owner=owner,
                repo=repo,
                state=state,
                sort=sort,
                direction=direction
            )
        server.register_command("issue.list", list_issues)
        
        # Register write operations if not in read-only mode
        if not self.read_only:
            # Register issue.create
            async def create_issue(owner: str, repo: str, title: str, body: Optional[str] = None, 
                              labels: Optional[List[str]] = None, assignees: Optional[List[str]] = None):
                return self.github_client.create_issue(
                    owner=owner,
                    repo=repo,
                    title=title,
                    body=body,
                    labels=labels,
                    assignees=assignees
                )
            server.register_command("issue.create", create_issue)
            
            # Register issue.add_labels
            async def add_issue_labels(owner: str, repo: str, issue_number: int, labels: List[str]):
                return self.github_client.add_issue_labels(
                    owner=owner,
                    repo=repo,
                    issue_number=issue_number,
                    labels=labels
                )
            server.register_command("issue.add_labels", add_issue_labels)
            
            # Register issue.remove_label
            async def remove_issue_label(owner: str, repo: str, issue_number: int, label: str):
                return self.github_client.remove_issue_label(
                    owner=owner,
                    repo=repo,
                    issue_number=issue_number,
                    label=label
                )
            server.register_command("issue.remove_label", remove_issue_label)
            
            # Register issue.comment
            async def add_issue_comment(owner: str, repo: str, issue_number: int, body: str):
                return self.github_client.add_issue_comment(
                    owner=owner,
                    repo=repo,
                    issue_number=issue_number,
                    body=body
                )
            server.register_command("issue.comment", add_issue_comment)


class PullRequestToolset(GithubToolset):
    """
    Pull request management toolset
    """
    
    def __init__(self, github_client: GitHubClient, read_only: bool = False):
        """
        Initialize pull request toolset
        """
        super().__init__(
            name="pullrequest",
            description="Pull request management tools",
            github_client=github_client,
            read_only=read_only
        )
        
        # Add pull request tools
        self.add_tool(Tool(
            name="pullrequest.list",
            description="List pull requests for a repository"
        ))
    
    def register_tools(self, server) -> None:
        """
        Register pull request tools with the server
        """
        # Register pullrequest.list
        async def list_pull_requests(owner: str, repo: str, state: str = "open", 
                                sort: str = "created", direction: str = "desc"):
            return self.github_client.get_pull_requests(
                owner=owner,
                repo=repo,
                state=state,
                sort=sort,
                direction=direction
            )
        server.register_command("pullrequest.list", list_pull_requests)


class ContentToolset(GithubToolset):
    """
    Content management toolset
    """
    
    def __init__(self, github_client: GitHubClient, read_only: bool = False):
        """
        Initialize content toolset
        """
        super().__init__(
            name="content",
            description="Content management tools",
            github_client=github_client,
            read_only=read_only
        )
        
        # Add content tools
        self.add_tool(Tool(
            name="content.get",
            description="Get file or directory content from a repository"
        ))
    
    def register_tools(self, server) -> None:
        """
        Register content tools with the server
        """
        # Register content.get
        async def get_content(owner: str, repo: str, path: str, ref: Optional[str] = None):
            return self.github_client.get_file_content(
                owner=owner,
                repo=repo,
                path=path,
                ref=ref
            )
        server.register_command("content.get", get_content)


class ProjectsToolset(GithubToolset):
    """
    Projects management toolset (GraphQL implementation)
    
    This toolset uses the GitHub GraphQL API to interact with the new
    Projects experience (ProjectsV2) since the classic Projects API
    has been deprecated.
    """
    
    def __init__(self, github_client: GitHubClient, read_only: bool = False):
        """
        Initialize projects toolset
        """
        super().__init__(
            name="projects",
            description="Project management tools (API v2)",
            github_client=github_client,
            read_only=read_only
        )
        
        # Add projects tools
        self.add_tool(Tool(
            name="projects.list",
            description="List projects in a repository (GraphQL)"
        ))
        
        self.add_tool(Tool(
            name="projects.get_columns",
            description="Get status options in a project (GraphQL)"
        ))
        
        self.add_tool(Tool(
            name="projects.get_cards",
            description="Get items with a specific status in a project (GraphQL)"
        ))
        
        # Add write operations if not in read-only mode
        if not read_only:
            self.add_tool(Tool(
                name="projects.move_card",
                description="Update an item's status in a project (GraphQL)"
            ))
    
    def register_tools(self, server) -> None:
        """
        Register projects tools with the server
        """
        # Register projects.list
        async def list_projects(owner: str, repo: str):
            return self.github_client.get_projects(owner, repo)
        server.register_command("projects.list", list_projects)
        
        # Register projects.get_columns
        async def get_project_columns(owner: str, repo: str, project_number: int):
            return self.github_client.get_project_columns(owner, repo, project_number)
        server.register_command("projects.get_columns", get_project_columns)
        
        # Register projects.get_cards
        async def get_project_cards(owner: str, repo: str, project_number: int, status_name: str):
            return self.github_client.get_project_cards(owner, repo, project_number, status_name)
        server.register_command("projects.get_cards", get_project_cards)
        
        # Register write operations if not in read-only mode
        if not self.read_only:
            # Register projects.move_card
            async def move_project_card(owner: str, repo: str, project_number: int, 
                                   item_id: str, status_value: str, position: str = "top"):
                return self.github_client.move_project_card(
                    owner=owner,
                    repo=repo,
                    project_number=project_number,
                    item_id=item_id,
                    status_value=status_value,
                    position=position
                )
            server.register_command("projects.move_card", move_project_card)


class UserToolset(GithubToolset):
    """
    User management toolset
    """
    
    def __init__(self, github_client: GitHubClient, read_only: bool = False):
        """
        Initialize user toolset
        """
        super().__init__(
            name="user",
            description="User management tools",
            github_client=github_client,
            read_only=read_only
        )
        
        # Add user tools
        self.add_tool(Tool(
            name="user.get",
            description="Get authenticated user information"
        ))
    
    def register_tools(self, server) -> None:
        """
        Register user tools with the server
        """
        # Register user.get
        async def get_user():
            return self.github_client.get_authenticated_user()
        server.register_command("user.get", get_user)


class ContextToolset(GithubToolset):
    """
    Context toolset
    """
    
    def __init__(self, github_client: GitHubClient, read_only: bool = False):
        """
        Initialize context toolset
        """
        super().__init__(
            name="context",
            description="Context tools",
            github_client=github_client,
            read_only=read_only
        )
        
        # Add context tools
        self.add_tool(Tool(
            name="context.provider",
            description="Get context provider information"
        ))
    
    def register_tools(self, server) -> None:
        """
        Register context tools with the server
        """
        # Register context.provider
        async def get_context_provider():
            return {
                "name": "github",
                "version": server.config.version if hasattr(server, "config") else "0.1.0"
            }
        server.register_command("context.provider", get_context_provider)


def init_toolsets(
    enabled_toolsets: List[str],
    read_only: bool,
    github_client: GitHubClient
) -> List[GithubToolset]:
    """
    Initialize GitHub toolsets
    
    Args:
        enabled_toolsets: List of toolset names to enable
        read_only: Whether to enable write operations
        github_client: GitHub client instance
    
    Returns:
        List of initialized toolsets
    """
    toolsets = []
    
    enable_all = "all" in enabled_toolsets
    
    # Initialize repository toolset
    if enable_all or "repository" in enabled_toolsets:
        toolsets.append(RepositoryToolset(github_client, read_only))
    
    # Initialize issue toolset
    if enable_all or "issue" in enabled_toolsets:
        toolsets.append(IssueToolset(github_client, read_only))
    
    # Initialize pull request toolset
    if enable_all or "pullrequest" in enabled_toolsets:
        toolsets.append(PullRequestToolset(github_client, read_only))
    
    # Initialize content toolset
    if enable_all or "content" in enabled_toolsets:
        toolsets.append(ContentToolset(github_client, read_only))
    
    # Initialize user toolset
    if enable_all or "user" in enabled_toolsets:
        toolsets.append(UserToolset(github_client, read_only))
    
    # Initialize projects toolset
    if enable_all or "projects" in enabled_toolsets:
        toolsets.append(ProjectsToolset(github_client, read_only))
    
    return toolsets


def register_tools(server, toolsets: List[GithubToolset]) -> None:
    """
    Register tools with the server
    
    Args:
        server: Server instance
        toolsets: List of toolsets to register
    """
    for toolset in toolsets:
        toolset.register_tools(server)
