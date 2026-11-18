# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""Main MCP server for Playwright browser automation."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import mcp.server.stdio
from mcp.server import Server

from .browser import BrowserManager, create_browser_manager
from .config import DEFAULT_CONFIG, ServerConfig
from .handlers import RequestHandlers

logger = logging.getLogger(__name__)


class PlaywrightMCPServer:
    """Playwright MCP Server with proper lifecycle management."""

    def __init__(self, config: ServerConfig = DEFAULT_CONFIG) -> None:
        self._config = config
        self._browser = create_browser_manager(config)
        self._handlers = RequestHandlers(self._browser, config.default_timeout)
        self._server = Server(config.name)
        self._handlers.register(self._server)

    @property
    def server(self) -> Server:
        return self._server

    @property
    def browser(self) -> BrowserManager:
        return self._browser

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        """Manage server lifecycle."""
        logger.info("Starting Playwright MCP server...")
        await self._browser.initialize()
        try:
            yield
        finally:
            logger.info("Shutting down Playwright MCP server...")
            await self._browser.close()

    async def run_stdio(self) -> None:
        """Run the server over stdio transport."""
        async with (
            mcp.server.stdio.stdio_server() as (read_stream, write_stream),
            self.lifespan(),
        ):
            await self._server.run(
                read_stream,
                write_stream,
                self._server.create_initialization_options(),
            )


def create_server(config: ServerConfig | None = None) -> PlaywrightMCPServer:
    """Factory function to create a configured server."""
    if config is None:
        config = DEFAULT_CONFIG
    return PlaywrightMCPServer(config)


async def main() -> None:
    """Main entry point for the server."""
    server = create_server()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())