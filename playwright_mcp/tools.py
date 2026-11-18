# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""Tool definitions for the Playwright MCP server."""

from mcp import types

TOOLS: list[types.Tool] = [
    types.Tool(
        name="navigate",
        description="Navigate to a URL",
        input_schema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to navigate to"},
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
            "required": ["url"],
        },
    ),
    types.Tool(
        name="click",
        description="Click on an element by selector",
        input_schema={
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of element to click"},
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
            "required": ["selector"],
        },
    ),
    types.Tool(
        name="type",
        description="Type text into an input element",
        input_schema={
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of input element"},
                "text": {"type": "string", "description": "Text to type"},
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
            "required": ["selector", "text"],
        },
    ),
    types.Tool(
        name="get_text",
        description="Get text content from an element",
        input_schema={
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of element"},
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
            "required": ["selector"],
        },
    ),
    types.Tool(
        name="get_page_content",
        description="Get the current page HTML content",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
        },
    ),
    types.Tool(
        name="take_screenshot",
        description="Take a screenshot of the current page or element",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID (optional)"},
                "selector": {"type": "string", "description": "CSS selector for element screenshot (optional)"},
                "full_page": {"type": "boolean", "description": "Take full page screenshot", "default": False},
            },
        },
    ),
    types.Tool(
        name="new_page",
        description="Create a new browser page",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Unique ID for the new page"},
            },
            "required": ["page_id"],
        },
    ),
    types.Tool(
        name="switch_page",
        description="Switch to a different browser page",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID to switch to"},
            },
            "required": ["page_id"],
        },
    ),
    types.Tool(
        name="get_pages",
        description="List all available browser pages",
        input_schema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="wait_for_selector",
        description="Wait for an element to be visible on the page",
        input_schema={
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector to wait for"},
                "page_id": {"type": "string", "description": "Page ID (optional)"},
                "timeout": {"type": "number", "description": "Timeout in milliseconds", "default": 30000},
                "state": {"type": "string", "enum": ["visible", "hidden", "attached", "detached"], "default": "visible"},
            },
            "required": ["selector"],
        },
    ),
    types.Tool(
        name="evaluate",
        description="Evaluate JavaScript in the page context",
        input_schema={
            "type": "object",
            "properties": {
                "script": {"type": "string", "description": "JavaScript code to evaluate"},
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
            "required": ["script"],
        },
    ),
    types.Tool(
        name="get_title",
        description="Get the page title",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
        },
    ),
    types.Tool(
        name="get_url",
        description="Get the current page URL",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
        },
    ),
    types.Tool(
        name="go_back",
        description="Navigate back in history",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
        },
    ),
    types.Tool(
        name="go_forward",
        description="Navigate forward in history",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
        },
    ),
    types.Tool(
        name="reload",
        description="Reload the current page",
        input_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID (optional)"},
            },
        },
    ),
]


def get_tools() -> list[types.Tool]:
    """Get the list of available tools."""
    return TOOLS