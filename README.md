# Playwright MCP Server

A Model Context Protocol (MCP) server that provides browser automation capabilities using Playwright. This server exposes a set of tools for navigating, interacting with, and extracting data from web pages.

## Features

- **Navigation**: Navigate to URLs, go back/forward, reload pages
- **Interaction**: Click elements, type text, wait for selectors
- **Extraction**: Get text content, page HTML, page title, URL
- **Screenshots**: Take full-page or element screenshots
- **Multi-page**: Create and switch between multiple browser pages
- **JavaScript Evaluation**: Execute arbitrary JS in page context

## Installation

```bash
# From source
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

## Usage

### As an MCP Server (stdio)

```bash
# Run with default settings (headless chromium)
playwright-mcp

# Run with custom options
playwright-mcp --headed --browser firefox --timeout 60000

# With additional browser args
playwright-mcp --browser-arg "--disable-web-security" --browser-arg "--no-sandbox"
```

### As a Library

```python
from playwright_mcp import create_server, ServerConfig, BrowserConfig

# Custom configuration
config = ServerConfig(
    browser=BrowserConfig(
        headless=True,
        browser_type="chromium",
    ),
    default_timeout=30000,
)

server = create_server(config)
await server.run_stdio()
```

## Available Tools

| Tool | Description |
|------|-------------|
| `navigate` | Navigate to a URL |
| `click` | Click on an element by selector |
| `type` | Type text into an input element |
| `get_text` | Get text content from an element |
| `get_page_content` | Get the current page HTML content |
| `take_screenshot` | Take a screenshot of page or element |
| `new_page` | Create a new browser page |
| `switch_page` | Switch to a different browser page |
| `get_pages` | List all available browser pages |
| `wait_for_selector` | Wait for an element to be visible |
| `evaluate` | Evaluate JavaScript in page context |
| `get_title` | Get the page title |
| `get_url` | Get the current page URL |
| `go_back` | Navigate back in history |
| `go_forward` | Navigate forward in history |
| `reload` | Reload the current page |

## Resources

The server exposes screenshot resources at URIs like `screenshot://{page_id}`.

## Configuration

### BrowserConfig

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `headless` | bool | `True` | Run browser in headless mode |
| `browser_type` | str | `"chromium"` | Browser engine (chromium, firefox, webkit) |
| `args` | tuple[str] | `()` | Additional browser launch arguments |
| `slow_mo` | float | `0.0` | Slow down operations by ms |
| `devtools` | bool | `False` | Open DevTools on launch |

### ServerConfig

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | str | `"playwright-mcp"` | Server name |
| `version` | str | `"0.2.0"` | Server version |
| `browser` | BrowserConfig | `BrowserConfig()` | Browser configuration |
| `default_timeout` | float | `30000.0` | Default timeout in ms |

## Development

```bash
# Run tests
pytest

# Type checking
mypy playwright_mcp

# Linting
ruff check playwright_mcp

# Format
ruff format playwright_mcp
```

## Architecture

```
playwright_mcp/
├── config.py       # Configuration dataclasses
├── browser.py      # Browser lifecycle management
├── tools.py        # Tool definitions (MCP schema)
├── executor.py     # Tool execution logic
├── handlers.py     # MCP request handlers
├── server.py       # Main server class
├── cli.py          # Command-line interface
└── __main__.py     # Entry point
```

## License

MIT