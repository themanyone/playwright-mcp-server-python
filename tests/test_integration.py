"""Integration tests for Playwright MCP server (requires browser)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


class TestBrowserLifecycle:
    """Test browser initialization and cleanup."""

    async def test_browser_initialize_close(self):
        from playwright_mcp.browser import BrowserManager
        from playwright_mcp.config import BrowserConfig

        manager = BrowserManager(BrowserConfig(headless=True))
        await manager.initialize()

        assert manager.is_initialized
        assert "default" in manager.pages
        assert manager.current_page_id == "default"

        await manager.close()

        assert not manager.is_initialized
        assert manager.pages == {}
        assert manager.current_page_id is None

    async def test_browser_context_manager(self):
        from playwright_mcp.browser import BrowserManager
        from playwright_mcp.config import BrowserConfig

        manager = BrowserManager(BrowserConfig(headless=True))
        async with manager.lifespan() as mgr:
            assert mgr is manager
            assert manager.is_initialized
        assert not manager.is_initialized


class TestToolExecution:
    """Test tool execution against real browser."""

    async def test_navigate_and_get_content(self):
        from playwright_mcp.browser import BrowserManager
        from playwright_mcp.config import BrowserConfig
        from playwright_mcp.executor import ToolExecutor

        manager = BrowserManager(BrowserConfig(headless=True))
        executor = ToolExecutor(manager)

        async with manager.lifespan():
            # Navigate
            result = await executor.execute("navigate", {"url": "https://example.com"})
            assert not result.is_error
            assert "Navigated to https://example.com" in result.content[0].text

            # Get content
            result = await executor.execute("get_page_content", {})
            assert not result.is_error
            assert "Example Domain" in result.content[0].text

    async def test_click_and_navigation(self):
        from playwright_mcp.browser import BrowserManager
        from playwright_mcp.config import BrowserConfig
        from playwright_mcp.executor import ToolExecutor

        manager = BrowserManager(BrowserConfig(headless=True))
        executor = ToolExecutor(manager)

        async with manager.lifespan():
            await executor.execute("navigate", {"url": "https://example.com"})
            result = await executor.execute("click", {"selector": "a"})
            # Example.com has a link to iana.org
            assert not result.is_error

    async def test_take_screenshot(self):
        from playwright_mcp.browser import BrowserManager
        from playwright_mcp.config import BrowserConfig
        from playwright_mcp.executor import ToolExecutor

        manager = BrowserManager(BrowserConfig(headless=True))
        executor = ToolExecutor(manager)

        async with manager.lifespan():
            await executor.execute("navigate", {"url": "https://example.com"})
            result = await executor.execute("take_screenshot", {})
            assert not result.is_error
            assert result.content[0].type == "image"
            assert result.content[0].mime_type == "image/png"
            # Verify base64 data
            import base64
            data = base64.b64decode(result.content[0].data)
            assert data[:8] == b"\x89PNG\r\n\x1a\n"  # PNG header

    async def test_multi_page(self):
        from playwright_mcp.browser import BrowserManager
        from playwright_mcp.config import BrowserConfig
        from playwright_mcp.executor import ToolExecutor

        manager = BrowserManager(BrowserConfig(headless=True))
        executor = ToolExecutor(manager)

        async with manager.lifespan():
            await executor.execute("navigate", {"url": "https://example.com"})
            await executor.execute("new_page", {"page_id": "page2"})
            await executor.execute("navigate", {"url": "https://example.org", "page_id": "page2"})

            pages_result = await executor.execute("get_pages", {})
            assert not pages_result.is_error
            import json
            pages = json.loads(pages_result.content[0].text)
            assert len(pages) == 2

            # Switch back to first page
            await executor.execute("switch_page", {"page_id": "default"})
            result = await executor.execute("get_url", {})
            assert "example.com" in result.content[0].text

    async def test_evaluate_javascript(self):
        from playwright_mcp.browser import BrowserManager
        from playwright_mcp.config import BrowserConfig
        from playwright_mcp.executor import ToolExecutor

        manager = BrowserManager(BrowserConfig(headless=True))
        executor = ToolExecutor(manager)

        async with manager.lifespan():
            await executor.execute("navigate", {"url": "https://example.com"})
            result = await executor.execute("evaluate", {"script": "document.title"})
            assert not result.is_error
            import json
            title = json.loads(result.content[0].text)
            assert title == "Example Domain"

    async def test_get_title_and_url(self):
        from playwright_mcp.browser import BrowserManager
        from playwright_mcp.config import BrowserConfig
        from playwright_mcp.executor import ToolExecutor

        manager = BrowserManager(BrowserConfig(headless=True))
        executor = ToolExecutor(manager)

        async with manager.lifespan():
            await executor.execute("navigate", {"url": "https://example.com"})

            title_result = await executor.execute("get_title", {})
            assert not title_result.is_error
            assert "Example Domain" in title_result.content[0].text

            url_result = await executor.execute("get_url", {})
            assert not url_result.is_error
            assert "example.com" in url_result.content[0].text


class TestServer:
    """Test the full MCP server."""

    async def test_server_list_tools(self):
        from playwright_mcp.server import create_server
        from playwright_mcp.config import ServerConfig, BrowserConfig

        config = ServerConfig(browser=BrowserConfig(headless=True))
        server = create_server(config)

        async with server.lifespan():
            from mcp.types import PaginatedRequestParams
            result = await server._handlers.handle_list_tools(None, PaginatedRequestParams())
            assert len(result.tools) > 15

    async def test_server_call_tool(self):
        from playwright_mcp.server import create_server
        from playwright_mcp.config import ServerConfig, BrowserConfig
        from mcp.types import CallToolRequestParams

        config = ServerConfig(browser=BrowserConfig(headless=True))
        server = create_server(config)

        async with server.lifespan():
            result = await server._handlers.handle_call_tool(
                None,
                CallToolRequestParams(name="navigate", arguments={"url": "https://example.com"})
            )
            assert not result.is_error


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])