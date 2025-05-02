"""
Standard IO server implementation for GitHub MCP
"""

import sys
import json
import asyncio
from typing import Any, Dict, Optional, Union
import traceback
from loguru import logger

from jsonrpcserver import method, async_dispatch
from jsonrpcserver.response import ErrorResponse, SuccessResponse
from github_mcp_server.config import Config
from github_mcp_server.github.github_client import GitHubClient
from github_mcp_server.models import (
    InitializeParams, 
    InitializeResult, 
    ServerInfo,
    ShutdownParams
)
from github_mcp_server.github.toolsets import init_toolsets, register_tools
from github_mcp_server.utils.log_io import LogIO


class StdioServer:
    """
    Standard IO server for GitHub MCP
    
    Communicates via standard input/output streams using JSON-RPC messages.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the stdio server
        """
        self.config = config
        self.github_client = GitHubClient(
            personal_access_token=config.personal_access_token,
            host=config.host,
            user_agent=f"github-mcp-server/{config.version}"
        )
        self.running = False
        self.initialized = False
        self.handlers = {}
        
        # Setup standard IO
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        
        # Configure logging for IO if enabled
        if config.enable_command_logging and config.log_file:
            self.io_logger = LogIO(self.stdin, self.stdout, config.log_file)
            self.stdin = self.io_logger
            self.stdout = self.io_logger
    
    async def read_request(self) -> str:
        """
        Read a JSON-RPC request from stdin
        """
        content_length = 0
        
        # Read headers
        while True:
            header = await self._readline()
            if not header:
                continue
            header = header.strip()
            if not header:
                break
                
            if header.startswith("Content-Length: "):
                content_length = int(header.split("Content-Length: ")[1])
        
        # Read content based on Content-Length
        if content_length > 0:
            content = await self._read(content_length)
            return content
        
        return ""
    
    async def _readline(self) -> str:
        """Read a line from stdin"""
        if hasattr(self.stdin, "readline"):
            return self.stdin.readline()
        
        # If readline is unavailable, read character by character
        result = ""
        while True:
            char = await self._read(1)
            if char == "\n" or not char:
                break
            result += char
        return result + "\n"
    
    async def _read(self, n: int) -> str:
        """Read n bytes from stdin"""
        if asyncio.iscoroutinefunction(self.stdin.read):
            return await self.stdin.read(n)
        return self.stdin.read(n)
    
    async def write_response(self, response: Union[str, Dict[str, Any]]) -> None:
        """
        Write a response to stdout
        """
        if isinstance(response, dict):
            response = json.dumps(response)
            
        headers = f"Content-Length: {len(response)}\r\n\r\n"
        content = f"{headers}{response}"
        
        if hasattr(self.stdout, "write"):
            self.stdout.write(content)
            self.stdout.flush()
        else:
            # Use async write if available
            await self.stdout.write(content)
            await self.stdout.flush()
    
    @method
    async def initialize(self, **params) -> InitializeResult:
        """
        Initialize the MCP server
        """
        init_params = InitializeParams(**params)
        
        # Update GitHub client user agent with client info
        client_info = init_params.client_info
        self.github_client.user_agent = (
            f"github-mcp-server/{self.config.version} "
            f"({client_info.name}/{client_info.version})"
        )
        
        # Initialize toolsets
        toolsets = init_toolsets(
            self.config.toolsets, 
            self.config.read_only,
            self.github_client
        )
        
        # Register tools with server
        register_tools(self, toolsets)
        
        # Mark as initialized
        self.initialized = True
        
        # Prepare and return result
        server_info = ServerInfo(
            name="github-mcp-server",
            version=self.config.version
        )
        
        return InitializeResult(serverInfo=server_info)
    
    @method
    async def shutdown(self, **params) -> Dict[str, Any]:
        """
        Shutdown the server
        """
        shutdown_params = ShutdownParams(**params)
        self.running = False
        return {}
    
    async def handle_request(self, request: str) -> None:
        """
        Handle a JSON-RPC request
        """
        try:
            # Parse request
            request_data = json.loads(request)
            
            # Dispatch to appropriate method
            response = await async_dispatch(request)
            
            # Write response
            if response and response.wanted:
                await self.write_response(response)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {request}")
            
            # Create error response
            error_response = ErrorResponse(
                id=None,
                error={"code": -32700, "message": "Parse error"}
            )
            await self.write_response(error_response)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            logger.error(traceback.format_exc())
            
            # Create error response
            error_response = ErrorResponse(
                id=None,
                error={"code": -32603, "message": f"Internal error: {str(e)}"}
            )
            await self.write_response(error_response)
    
    async def run_async(self) -> None:
        """
        Run the server asynchronously
        """
        self.running = True
        
        # Print server info to stderr
        print("GitHub MCP Server running on stdio", file=sys.stderr)
        
        while self.running:
            try:
                # Read request
                request = await self.read_request()
                if not request:
                    await asyncio.sleep(0.1)
                    continue
                
                # Handle request
                await self.handle_request(request)
            except Exception as e:
                logger.error(f"Error in server loop: {e}")
                logger.error(traceback.format_exc())
                self.running = False
    
    def run(self) -> None:
        """
        Run the server
        """
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            logger.info("Server stopped by keyboard interrupt")
        except Exception as e:
            logger.error(f"Error running server: {e}")
            logger.error(traceback.format_exc())
            raise
