"""Unit tests for Playwright MCP server."""

from __future__ import annotations

import pytest

from playwright_mcp.config import BrowserConfig, ServerConfig, DEFAULT_CONFIG
from playwright_mcp.tools import get_tools, TOOLS
from playwright_mcp.browser import BrowserManager


class TestConfig:
    """Test configuration dataclasses."""

    def test_browser_config_defaults(self):
        config = BrowserConfig()
        assert config.headless is True
        assert config.browser_type == "chromium"
        assert config.args == ()
        assert config.slow_mo == 0.0

    def test_browser_config_custom(self):
        config = BrowserConfig(
            headless=False,
            browser_type="firefox",
            args=("--no-sandbox",),
            slow_mo=100.0,
        )
        assert config.headless is False
        assert config.browser_type == "firefox"
        assert config.args == ("--no-sandbox",)
        assert config.slow_mo == 100.0

    def test_server_config_defaults(self):
        config = ServerConfig()
        assert config.name == "playwright-mcp"
        assert config.version == "0.2.0"
        assert isinstance(config.browser, BrowserConfig)
        assert config.default_timeout == 30000.0

    def test_default_config(self):
        assert isinstance(DEFAULT_CONFIG, ServerConfig)
        assert DEFAULT_CONFIG.name == "playwright-mcp"


class TestTools:
    """Test tool definitions."""

    def test_tools_list_not_empty(self):
        tools = get_tools()
        assert len(tools) > 0
        assert tools is TOOLS  # Same reference

    def test_tool_names_unique(self):
        tools = get_tools()
        names = [t.name for t in tools]
        assert len(names) == len(set(names))

    def test_required_tools_exist(self):
        tools = get_tools()
        names = {t.name for t in tools}
        required = {
            "navigate", "click", "type", "get_text",
            "get_page_content", "take_screenshot",
            "new_page", "switch_page", "get_pages",
            "wait_for_selector", "evaluate",
            "get_title", "get_url", "go_back",
            "go_forward", "reload",
        }
        assert required.issubset(names)

    def test_tool_schemas_valid(self):
        for tool in get_tools():
            assert tool.name
            assert tool.description
            assert tool.input_schema
            assert tool.input_schema["type"] == "object"
            assert "properties" in tool.input_schema


class TestBrowserManager:
    """Test browser manager (without actual browser)."""

    def test_initial_state(self):
        manager = BrowserManager(BrowserConfig())
        assert not manager.is_initialized
        assert manager.pages == {}
        assert manager.current_page_id is None

    def test_get_page_raises_when_not_initialized(self):
        manager = BrowserManager(BrowserConfig())
        with pytest.raises(ValueError, match="No pages available"):
            manager.get_page()

    def test_get_page_raises_for_unknown_id(self):
        manager = BrowserManager(BrowserConfig())
        # Manually set up pages dict to test the logic
        manager._pages = {"page1": object()}
        with pytest.raises(ValueError, match="Page not found"):
            manager.get_page("unknown")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])