# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""Tool execution logic for Playwright MCP server."""

from __future__ import annotations

import base64
import json
from typing import Any

from mcp import types
from playwright.async_api import Page

from .browser import BrowserManager


class ToolExecutor:
    """Executes Playwright tools against a browser manager."""

    def __init__(self, browser_manager: BrowserManager, default_timeout: float = 30000.0) -> None:
        self._browser = browser_manager
        self._default_timeout = default_timeout

    async def execute(self, name: str, arguments: dict[str, Any]) -> types.CallToolResult:
        """Execute a tool by name with arguments."""
        try:
            handler = getattr(self, f"_handle_{name}", None)
            if handler is None:
                raise ValueError(f"Unknown tool: {name}")
            result: types.CallToolResult = await handler(arguments)
            return result
        except Exception as e:  # noqa: BLE001
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Error: {e!s}")],
                is_error=True,
            )

    def _get_page(self, page_id: str | None = None) -> Page:
        return self._browser.get_page(page_id)

    async def _handle_navigate(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        await page.goto(args["url"], timeout=self._default_timeout)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Navigated to {args['url']}")]
        )

    async def _handle_click(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        await page.click(args["selector"], timeout=args.get("timeout", self._default_timeout))
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Clicked {args['selector']}")]
        )

    async def _handle_type(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        await page.fill(args["selector"], args["text"], timeout=self._default_timeout)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Typed into {args['selector']}")]
        )

    async def _handle_get_text(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        text = await page.locator(args["selector"]).text_content(timeout=self._default_timeout)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=text or "")]
        )

    async def _handle_get_page_content(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        content = await page.content()
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=content)]
        )

    async def _handle_take_screenshot(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        selector = args.get("selector")
        full_page = args.get("full_page", False)

        if selector:
            screenshot = await page.locator(selector).screenshot()
        elif full_page:
            screenshot = await page.screenshot(full_page=True)
        else:
            screenshot = await page.screenshot()

        b64 = base64.b64encode(screenshot).decode()
        return types.CallToolResult(
            content=[types.ImageContent(type="image", data=b64, mime_type="image/png")]
        )

    async def _handle_new_page(self, args: dict[str, Any]) -> types.CallToolResult:
        page_id = args["page_id"]
        await self._browser.create_page(page_id)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Created new page: {page_id}")]
        )

    async def _handle_switch_page(self, args: dict[str, Any]) -> types.CallToolResult:
        page_id = args["page_id"]
        if page_id not in self._browser.pages:
            raise ValueError(f"Page not found: {page_id}")
        self._browser.current_page_id = page_id
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Switched to page: {page_id}")]
        )

    async def _handle_get_pages(self, args: dict[str, Any]) -> types.CallToolResult:
        page_list = [
            {"id": pid, "url": p.url, "title": await p.title()}
            for pid, p in self._browser.pages.items()
        ]
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(page_list, indent=2))]
        )

    async def _handle_wait_for_selector(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        selector = args["selector"]
        timeout = args.get("timeout", self._default_timeout)
        state = args.get("state", "visible")
        await page.wait_for_selector(selector, state=state, timeout=timeout)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Element {selector} is {state}")]
        )

    async def _handle_evaluate(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        result = await page.evaluate(args["script"])
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(result, default=str))]
        )

    async def _handle_get_title(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        title = await page.title()
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=title)]
        )

    async def _handle_get_url(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=page.url)]
        )

    async def _handle_go_back(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        await page.go_back(timeout=self._default_timeout)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="Navigated back")]
        )

    async def _handle_go_forward(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        await page.go_forward(timeout=self._default_timeout)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="Navigated forward")]
        )

    async def _handle_reload(self, args: dict[str, Any]) -> types.CallToolResult:
        page = self._get_page(args.get("page_id"))
        await page.reload(timeout=self._default_timeout)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="Page reloaded")]
        )