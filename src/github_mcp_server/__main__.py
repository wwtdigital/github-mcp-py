"""
Main entry point for the GitHub MCP Server
"""

import sys
import typer
from typing import List, Optional
import os
from loguru import logger
import signal
from github_mcp_server.config import Config
from github_mcp_server.stdio_server import StdioServer
from github_mcp_server.http_server import HttpServer

app = typer.Typer(
    name="github-mcp-server",
    help="GitHub MCP server that handles various tools and resources"
)

# Get version info from package
__version__ = "0.1.0"
__commit__ = "dev"
__build_date__ = "2025-05-02"

VERSION_INFO = f"Version: {__version__}\nCommit: {__commit__}\nBuild Date: {__build_date__}"


@app.callback()
def callback(
    ctx: typer.Context,
    toolsets: List[str] = typer.Option(
        ["all"], 
        help="An optional comma separated list of groups of tools to allow, defaults to enabling all"
    ),
    dynamic_toolsets: bool = typer.Option(
        False, 
        help="Enable dynamic toolsets"
    ),
    read_only: bool = typer.Option(
        False, 
        help="Restrict the server to read-only operations"
    ),
    log_file: Optional[str] = typer.Option(
        None, 
        help="Path to log file"
    ),
    enable_command_logging: bool = typer.Option(
        False, 
        help="When enabled, the server will log all command requests and responses to the log file"
    ),
    export_translations: bool = typer.Option(
        False, 
        help="Save translations to a JSON file"
    ),
    gh_host: Optional[str] = typer.Option(
        None, 
        help="Specify the GitHub hostname (for GitHub Enterprise etc.)"
    ),
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        help="Show version and exit", 
        callback=lambda v: print(VERSION_INFO) or sys.exit(0) if v else None
    ),
):
    """
    GitHub MCP Server
    """
    # Initialize configuration
    config = Config()
    config.toolsets = toolsets
    config.dynamic_toolsets = dynamic_toolsets
    config.read_only = read_only
    config.log_file = log_file
    config.enable_command_logging = enable_command_logging
    config.export_translations = export_translations
    config.host = gh_host

    # Configure logging
    if log_file:
        logger.add(log_file, rotation="10 MB", level="DEBUG")

    # Make config available to commands
    ctx.obj = config


@app.command()
def stdio(
    ctx: typer.Context,
):
    """
    Start a server that communicates via standard input/output streams using JSON-RPC messages.
    """
    config = ctx.obj
    
    # Get GitHub token from environment
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        logger.error("GITHUB_PERSONAL_ACCESS_TOKEN not set")
        sys.exit(1)
    
    config.personal_access_token = token
    
    # Setup signal handling
    def signal_handler(sig, frame):
        logger.info("Shutting down server...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start stdio server
    logger.info("GitHub MCP Server running on stdio")
    try:
        server = StdioServer(config)
        server.run()
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


@app.command()
def http(
    ctx: typer.Context,
    port: int = typer.Option(
        8080, 
        help="Port to listen on"
    ),
    host: str = typer.Option(
        "0.0.0.0", 
        help="Host to bind to"
    ),
):
    """
    Start an HTTP server that listens for MCP requests.
    """
    config = ctx.obj
    
    # Get GitHub token from environment
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        logger.error("GITHUB_PERSONAL_ACCESS_TOKEN not set")
        sys.exit(1)
    
    config.personal_access_token = token
    
    # Start HTTP server
    logger.info(f"GitHub MCP Server running on http://{host}:{port}")
    try:
        server = HttpServer(config)
        server.run(host=host, port=port)
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


def main():
    """
    Main entry point
    """
    app()


if __name__ == "__main__":
    main()
