# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""Browser lifecycle management."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from .config import BrowserConfig, ServerConfig


class BrowserManager:
    """Manages Playwright browser lifecycle and page pool."""

    def __init__(self, config: BrowserConfig) -> None:
        self._config = config
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._pages: dict[str, Page] = {}
        self._current_page_id: str | None = None
        self._lock = asyncio.Lock()

    @property
    def is_initialized(self) -> bool:
        return self._browser is not None and self._browser.is_connected()

    @property
    def pages(self) -> dict[str, Page]:
        return self._pages

    @property
    def current_page_id(self) -> str | None:
        return self._current_page_id

    @current_page_id.setter
    def current_page_id(self, value: str | None) -> None:
        self._current_page_id = value

    async def initialize(self) -> None:
        """Initialize browser, context, and default page."""
        async with self._lock:
            if self.is_initialized:
                return

            self._playwright = await async_playwright().start()
            browser_type = getattr(self._playwright, self._config.browser_type)
            self._browser = await browser_type.launch(
                headless=self._config.headless,
                args=list(self._config.args),
                slow_mo=self._config.slow_mo,
            )
            self._context = await self._browser.new_context()
            default_page = await self._context.new_page()
            self._pages["default"] = default_page
            self._current_page_id = "default"

    async def close(self) -> None:
        """Clean up browser resources."""
        async with self._lock:
            if self._context:
                await self._context.close()
                self._context = None
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            self._pages.clear()
            self._current_page_id = None

    def get_page(self, page_id: str | None = None) -> Page:
        """Get a page by ID, defaulting to current page."""
        if page_id is None:
            page_id = self._current_page_id
        if page_id is None:
            if self._pages:
                page_id = next(iter(self._pages))
            else:
                raise ValueError("No pages available. Call initialize() first.")
        if page_id not in self._pages:
            raise ValueError(f"Page not found: {page_id}")
        return self._pages[page_id]

    async def create_page(self, page_id: str) -> Page:
        """Create a new page with the given ID."""
        if not self._context:
            raise RuntimeError("Browser not initialized")
        page = await self._context.new_page()
        self._pages[page_id] = page
        self._current_page_id = page_id
        return page

    def remove_page(self, page_id: str) -> bool:
        """Remove a page from the pool."""
        if page_id in self._pages:
            # Don't actually close the page, just remove from pool
            # The context will clean up on close()
            del self._pages[page_id]
            if self._current_page_id == page_id:
                self._current_page_id = next(iter(self._pages)) if self._pages else None
            return True
        return False

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[BrowserManager]:
        """Context manager for browser lifecycle."""
        await self.initialize()
        try:
            yield self
        finally:
            await self.close()


def create_browser_manager(config: ServerConfig | None = None) -> BrowserManager:
    """Factory function to create a browser manager."""
    if config is None:
        config = ServerConfig()
    return BrowserManager(config.browser)