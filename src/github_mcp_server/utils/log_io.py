"""
Logging utilities for IO operations
"""

import sys
import json
from typing import Optional, Dict, Any, Union, IO
from loguru import logger


class LogIO:
    """
    Logging wrapper for stdin/stdout streams
    
    Logs all input and output when enabled.
    """
    
    def __init__(self, stdin: IO, stdout: IO, log_file: str):
        """
        Initialize LogIO
        
        Args:
            stdin: Input stream to wrap
            stdout: Output stream to wrap
            log_file: Path to log file
        """
        self.stdin = stdin
        self.stdout = stdout
        self.log_file = log_file
        
        # Configure logger for this module
        logger.add(log_file, rotation="10 MB", filter=lambda record: record["extra"].get("io_log", False))
    
    def read(self, n: int = -1) -> str:
        """
        Read n bytes from stdin and log
        """
        content = self.stdin.read(n)
        if content:
            logger_with_context = logger.bind(io_log=True)
            logger_with_context.debug(f"STDIN: {content}")
        return content
    
    def readline(self) -> str:
        """
        Read a line from stdin and log
        """
        line = self.stdin.readline()
        if line:
            logger_with_context = logger.bind(io_log=True)
            logger_with_context.debug(f"STDIN: {line}")
        return line
    
    def write(self, content: str) -> int:
        """
        Write content to stdout and log
        """
        if content:
            logger_with_context = logger.bind(io_log=True)
            logger_with_context.debug(f"STDOUT: {content}")
        return self.stdout.write(content)
    
    def flush(self) -> None:
        """
        Flush stdout
        """
        self.stdout.flush()
    
    def log_request(self, request: Union[str, Dict[str, Any]]) -> None:
        """
        Log a JSON-RPC request
        """
        if isinstance(request, str):
            try:
                request = json.loads(request)
            except json.JSONDecodeError:
                # Not valid JSON, log as is
                pass
        
        logger_with_context = logger.bind(io_log=True)
        logger_with_context.debug(f"REQUEST: {request}")
    
    def log_response(self, response: Union[str, Dict[str, Any]]) -> None:
        """
        Log a JSON-RPC response
        """
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                # Not valid JSON, log as is
                pass
        
        logger_with_context = logger.bind(io_log=True)
        logger_with_context.debug(f"RESPONSE: {response}")
