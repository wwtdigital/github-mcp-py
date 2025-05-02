"""
Data models for the GitHub MCP server
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class ClientInfo(BaseModel):
    """Client information"""
    name: str
    version: str


class InitializeParams(BaseModel):
    """Parameters for initialize request"""
    client_info: ClientInfo = Field(..., alias="clientInfo")


class InitializeRequest(BaseModel):
    """Initialize request"""
    jsonrpc: str = "2.0"
    method: str = "initialize"
    id: Union[int, str]
    params: InitializeParams


class ServerInfo(BaseModel):
    """Server information"""
    name: str = "github-mcp-server"
    version: str


class Capability(BaseModel):
    """Server capability"""
    name: str
    description: str
    version: str = "1.0.0"


class InitializeResult(BaseModel):
    """Result of initialize request"""
    server_info: ServerInfo = Field(..., alias="serverInfo")
    capabilities: List[Capability] = Field(default_factory=list, alias="capabilities")
    available_tools: List[str] = Field(default_factory=list, alias="availableTools")


class InitializeResponse(BaseModel):
    """Initialize response"""
    jsonrpc: str = "2.0"
    id: Union[int, str]
    result: InitializeResult


class ShutdownParams(BaseModel):
    """Parameters for shutdown request"""
    pass


class ShutdownRequest(BaseModel):
    """Shutdown request"""
    jsonrpc: str = "2.0"
    method: str = "shutdown"
    id: Union[int, str]
    params: ShutdownParams = ShutdownParams()


class ShutdownResult(BaseModel):
    """Result of shutdown request"""
    pass


class ShutdownResponse(BaseModel):
    """Shutdown response"""
    jsonrpc: str = "2.0"
    id: Union[int, str]
    result: ShutdownResult = ShutdownResult()


class ExecuteCommandParams(BaseModel):
    """Parameters for executeCommand request"""
    command: str
    arguments: Optional[List[Any]] = None


class ExecuteCommandRequest(BaseModel):
    """Execute command request"""
    jsonrpc: str = "2.0"
    method: str = "executeCommand"
    id: Union[int, str]
    params: ExecuteCommandParams


class ExecuteCommandResult(BaseModel):
    """Result of executeCommand request"""
    value: Any


class ExecuteCommandResponse(BaseModel):
    """Execute command response"""
    jsonrpc: str = "2.0"
    id: Union[int, str]
    result: ExecuteCommandResult


class ErrorResponse(BaseModel):
    """Error response"""
    jsonrpc: str = "2.0"
    id: Union[int, str, None]
    error: Dict[str, Any]


# Tool definitions
class Tool(BaseModel):
    """Base tool model"""
    name: str
    description: str


class Resource(BaseModel):
    """Base resource model"""
    name: str
    description: str


class Toolset(BaseModel):
    """Group of tools"""
    name: str
    description: str
    tools: List[Tool] = []
    resources: List[Resource] = []
