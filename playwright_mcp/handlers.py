# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""MCP request handlers for the Playwright server."""

from __future__ import annotations

import base64

from mcp import types
from mcp.server import Server
from mcp.server.context import ServerRequestContext

from .browser import BrowserManager
from .executor import ToolExecutor
from .tools import get_tools


class RequestHandlers:
    """Handles MCP requests by delegating to browser manager and tool executor."""

    def __init__(
        self,
        browser_manager: BrowserManager,
        default_timeout: float = 30000.0,
    ) -> None:
        self._browser = browser_manager
        self._executor = ToolExecutor(browser_manager, default_timeout)

    async def _ensure_initialized(self) -> None:
        """Lazily initialize the browser on first tool call."""
        if not self._browser.is_initialized:
            await self._browser.initialize()

    async def handle_list_tools(
        self, ctx: ServerRequestContext, params: types.PaginatedRequestParams
    ) -> types.ListToolsResult:
        """List available tools."""
        return types.ListToolsResult(tools=get_tools())

    async def handle_call_tool(
        self, ctx: ServerRequestContext, params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        """Execute a tool."""
        await self._ensure_initialized()
        return await self._executor.execute(params.name, params.arguments or {})

    async def handle_list_resources(
        self, ctx: ServerRequestContext, params: types.PaginatedRequestParams
    ) -> types.ListResourcesResult:
        """List available resources (screenshots)."""
        await self._ensure_initialized()
        resources = []
        for page_id, page in self._browser.pages.items():
            resources.append(
                types.Resource(
                    uri=f"screenshot://{page_id}",
                    name=f"Screenshot: {page.url}",
                    description=f"Current screenshot of page at {page.url}",
                    mime_type="image/png",
                )
            )
        return types.ListResourcesResult(resources=resources)

    async def handle_read_resource(
        self, ctx: ServerRequestContext, params: types.ReadResourceRequestParams
    ) -> types.ReadResourceResult:
        """Read a screenshot resource."""
        await self._ensure_initialized()
        uri = params.uri
        if not uri.startswith("screenshot://"):
            raise ValueError(f"Unsupported URI scheme: {uri}")

        page_id = uri.replace("screenshot://", "")
        if page_id not in self._browser.pages:
            raise ValueError(f"Page not found: {page_id}")

        screenshot = await self._browser.pages[page_id].screenshot()
        return types.ReadResourceResult(
            contents=[
                types.BlobResourceContents(
                    uri=uri,
                    mime_type="image/png",
                    blob=base64.b64encode(screenshot).decode(),
                )
            ]
        )

    async def handle_list_resource_templates(
        self, ctx: ServerRequestContext, params: types.PaginatedRequestParams
    ) -> types.ListResourceTemplatesResult:
        """List resource templates."""
        return types.ListResourceTemplatesResult(resource_templates=[])

    def register(self, server: Server) -> None:
        """Register all handlers with the MCP server."""
        server.add_request_handler("tools/list", types.PaginatedRequestParams, self.handle_list_tools)
        server.add_request_handler("tools/call", types.CallToolRequestParams, self.handle_call_tool)
        server.add_request_handler("resources/list", types.PaginatedRequestParams, self.handle_list_resources)
        server.add_request_handler("resources/read", types.ReadResourceRequestParams, self.handle_read_resource)
        server.add_request_handler("resources/templates/list", types.PaginatedRequestParams, self.handle_list_resource_templates)