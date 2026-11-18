# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""Entry point for running the Playwright MCP server."""

import asyncio

from .server import main

if __name__ == "__main__":
    asyncio.run(main())