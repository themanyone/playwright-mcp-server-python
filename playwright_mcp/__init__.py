# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""Playwright MCP Server - Browser automation via Model Context Protocol."""

from .browser import BrowserManager, create_browser_manager
from .config import DEFAULT_CONFIG, BrowserConfig, ServerConfig
from .executor import ToolExecutor
from .handlers import RequestHandlers
from .server import PlaywrightMCPServer, create_server, main
from .tools import TOOLS, get_tools

__version__ = "0.2.1"
__all__ = [
    "DEFAULT_CONFIG",
    "TOOLS",
    "BrowserConfig",
    "BrowserManager",
    "PlaywrightMCPServer",
    "RequestHandlers",
    "ServerConfig",
    "ToolExecutor",
    "create_browser_manager",
    "create_server",
    "get_tools",
    "main",
]
