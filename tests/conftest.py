"""Pytest configuration for Playwright MCP tests."""

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require browser)"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()