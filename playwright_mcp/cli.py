# Copyright (c) 2024 Playwright MCP Server Contributors
# Licensed under the MIT License - see LICENSE file for details
"""Command-line interface for the Playwright MCP server."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from .config import DEFAULT_CONFIG, BrowserConfig, ServerConfig
from .server import create_server

logger = logging.getLogger(__name__)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Playwright MCP Server - Browser automation via Model Context Protocol",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        default=None,
        help="Run browser in headless mode (default: True)",
    )
    parser.add_argument(
        "--headed",
        action="store_false",
        dest="headless",
        help="Run browser in headed mode",
    )
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default=None,
        help="Browser type to use",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Default timeout in milliseconds",
    )
    
    parser.add_argument(
        "--slow-mo",
        type=float,
        default=None,
        help="Slow down operations by specified milliseconds",
    )
    parser.add_argument(
        "--browser-arg",
        action="append",
        default=None,
        help="Additional browser launch arguments (can be repeated)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.2.0",
    )

    return parser.parse_args(args)


def build_config(args: argparse.Namespace) -> ServerConfig:
    """Build server config from parsed arguments."""
    browser_config = BrowserConfig()

    if args.headless is not None:
        browser_config = BrowserConfig(
            headless=args.headless,
            browser_type=args.browser or DEFAULT_CONFIG.browser.browser_type,
            args=tuple(args.browser_arg) if args.browser_arg else DEFAULT_CONFIG.browser.args,
            slow_mo=args.slow_mo if args.slow_mo is not None else DEFAULT_CONFIG.browser.slow_mo,
        )
    elif args.browser is not None or args.browser_arg is not None or args.slow_mo is not None:
        browser_config = BrowserConfig(
            headless=DEFAULT_CONFIG.browser.headless,
            browser_type=args.browser or DEFAULT_CONFIG.browser.browser_type,
            args=tuple(args.browser_arg) if args.browser_arg else DEFAULT_CONFIG.browser.args,
            slow_mo=args.slow_mo if args.slow_mo is not None else DEFAULT_CONFIG.browser.slow_mo,
        )

    return ServerConfig(
        name=DEFAULT_CONFIG.name,
        version=DEFAULT_CONFIG.version,
        browser=browser_config,
        default_timeout=args.timeout if args.timeout is not None else DEFAULT_CONFIG.default_timeout,
    )


def main(args: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parsed = parse_args(args)

    logging.basicConfig(
        level=parsed.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = build_config(parsed)
    server = create_server(config)

    try:
        asyncio.run(server.run_stdio())
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 130
    except Exception:
        logger.exception("Server error")
        return 1


if __name__ == "__main__":
    sys.exit(main())