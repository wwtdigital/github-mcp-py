"""
Configuration module for GitHub MCP server
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
from loguru import logger

# Get the project root directory
project_root = Path(__file__).parent.parent.parent.absolute()

# Load environment variables from .env file if it exists
dotenv_path = project_root / ".env"
if dotenv_path.exists():
    logger.info(f"Loading environment from {dotenv_path}")
    # Use override=True to ensure .env values take precedence over existing environment variables
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    logger.warning(f".env file not found at {dotenv_path}")



@dataclass
class Config:
    """
    Configuration class for GitHub MCP server
    """
    # GitHub configuration
    personal_access_token: str = field(default_factory=lambda: os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", ""))
    host: Optional[str] = field(default_factory=lambda: os.environ.get("GITHUB_HOST", ""))
    
    # Server configuration
    read_only: bool = field(default_factory=lambda: os.environ.get("GITHUB_READ_ONLY", "false").lower() == "true")
    log_file: Optional[str] = field(default_factory=lambda: os.environ.get("GITHUB_LOG_FILE", None))
    enable_command_logging: bool = field(
        default_factory=lambda: os.environ.get("GITHUB_ENABLE_COMMAND_LOGGING", "false").lower() == "true"
    )
    export_translations: bool = field(
        default_factory=lambda: os.environ.get("GITHUB_EXPORT_TRANSLATIONS", "false").lower() == "true"
    )
    
    # Toolsets configuration
    toolsets: List[str] = field(default_factory=lambda: os.environ.get("GITHUB_TOOLSETS", "all").split(","))
    dynamic_toolsets: bool = field(
        default_factory=lambda: os.environ.get("GITHUB_DYNAMIC_TOOLSETS", "false").lower() == "true"
    )
    
    # Mock mode for testing without a real GitHub token
    mock_mode: bool = field(
        default_factory=lambda: os.environ.get("GITHUB_MOCK_MODE", "false").lower() == "true"
    )
    
    # Version information
    version: str = "0.1.0"
    commit: str = "dev"
    build_date: str = "2025-05-02"
    
    def get_version_string(self) -> str:
        """
        Get formatted version information
        """
        return f"Version: {self.version}\nCommit: {self.commit}\nBuild Date: {self.build_date}"
