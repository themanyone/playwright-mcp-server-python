# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""Configuration for the Playwright MCP server."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BrowserConfig:
    """Browser launch configuration."""
    headless: bool = True
    browser_type: str = "chromium"  # chromium, firefox, webkit
    args: tuple[str, ...] = field(default_factory=tuple)
    slow_mo: float = 0.0


@dataclass(frozen=True)
class ServerConfig:
    """Server configuration."""
    name: str = "playwright-mcp"
    version: str = "0.2.0"
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    default_timeout: float = 30000.0  # ms


DEFAULT_CONFIG = ServerConfig()