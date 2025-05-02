"""
HTTP server implementation for GitHub MCP
"""

import json
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from github_mcp_server.config import Config
from github_mcp_server.github.github_client import GitHubClient
from github_mcp_server.models import (
    InitializeParams,
    InitializeResult,
    ServerInfo,
    Capability,
    ExecuteCommandParams,
    ExecuteCommandResult
)
from github_mcp_server.github.toolsets import init_toolsets, register_tools


class HttpServer:
    """
    HTTP server for GitHub MCP
    
    Provides HTTP API endpoints for MCP functionality.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the HTTP server
        """
        self.config = config
        self.github_client = GitHubClient(
            personal_access_token=config.personal_access_token,
            host=config.host,
            user_agent=f"github-mcp-server/{config.version}"
        )
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="GitHub MCP Server",
            description="GitHub Message Control Protocol (MCP) server for Windsurf integration",
            version=config.version
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
        
        # Initialize toolsets
        self.toolsets = init_toolsets(
            config.toolsets,
            config.read_only,
            self.github_client
        )
        
        # Store commands dictionary
        self.commands = {}
        
        # Register tools
        register_tools(self, self.toolsets)
    
    def _register_routes(self) -> None:
        """
        Register HTTP routes
        """
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "name": "github-mcp-server",
                "version": self.config.version,
                "description": "GitHub MCP Server (HTTP)"
            }
        
        @self.app.get("/capabilities")
        async def get_capabilities():
            """Get server capabilities and available tools"""
            # Collect all available capabilities
            capabilities = [
                Capability(
                    name="github",
                    description="GitHub API integration",
                    version=self.config.version
                ),
                Capability(
                    name="jsonrpc",
                    description="JSON-RPC protocol support",
                    version="2.0"
                ),
                Capability(
                    name="http",
                    description="HTTP API endpoints",
                    version="1.0"
                )
            ]
            
            # Collect all available tools from toolsets
            available_tools = []
            for toolset in self.toolsets:
                toolset_tools = []
                for tool in toolset.tools:
                    toolset_tools.append({
                        "name": tool.name,
                        "description": tool.description
                    })
                available_tools.append({
                    "name": toolset.name,
                    "description": toolset.description,
                    "tools": toolset_tools
                })
            
            return {
                "capabilities": [cap.dict() for cap in capabilities],
                "toolsets": available_tools
            }
        
        @self.app.post("/initialize")
        async def initialize(params: InitializeParams):
            """Initialize the server"""
            # Update GitHub client user agent with client info
            client_info = params.client_info
            self.github_client.user_agent = (
                f"github-mcp-server/{self.config.version} "
                f"({client_info.name}/{client_info.version})"
            )
            
            # Collect all available capabilities
            capabilities = [
                Capability(
                    name="github",
                    description="GitHub API integration",
                    version=self.config.version
                ),
                Capability(
                    name="jsonrpc",
                    description="JSON-RPC protocol support",
                    version="2.0"
                ),
                Capability(
                    name="http",
                    description="HTTP API endpoints",
                    version="1.0"
                )
            ]
            
            # Collect all available tools
            available_tools = []
            for toolset in self.toolsets:
                for tool in toolset.tools:
                    available_tools.append(tool.name)
            
            # Prepare and return result
            server_info = ServerInfo(
                name="github-mcp-server",
                version=self.config.version
            )
            
            return InitializeResult(
                serverInfo=server_info,
                capabilities=capabilities,
                availableTools=available_tools
            )
        
        @self.app.post("/executeCommand")
        async def execute_command(params: ExecuteCommandParams):
            """Execute a command"""
            command = params.command
            arguments = params.arguments or []
            
            if command not in self.commands:
                raise HTTPException(status_code=404, message=f"Command '{command}' not found")
            
            try:
                result = await self.commands[command](*arguments)
                return ExecuteCommandResult(value=result)
            except Exception as e:
                logger.error(f"Error executing command {command}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/jsonrpc")
        async def jsonrpc_endpoint(request: Request):
            """JSON-RPC endpoint"""
            try:
                # Parse request
                data = await request.json()
                
                method = data.get("method")
                params = data.get("params", {})
                request_id = data.get("id")
                
                # Handle methods
                if method == "initialize":
                    result = await initialize(InitializeParams(**params))
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                elif method == "shutdown":
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {}
                    }
                elif method == "executeCommand":
                    command_params = ExecuteCommandParams(**params)
                    result = await execute_command(command_params)
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method '{method}' not found"
                            }
                        }
                    )
            except Exception as e:
                logger.error(f"Error handling JSON-RPC request: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "jsonrpc": "2.0",
                        "id": data.get("id") if "data" in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                )
    
    def register_command(self, name: str, handler) -> None:
        """
        Register a command handler
        """
        self.commands[name] = handler
    
    def run(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """
        Run the HTTP server
        """
        uvicorn.run(self.app, host=host, port=port)
