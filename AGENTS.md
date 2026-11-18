# AGENTS.md - Playwright MCP Server

This document provides essential context for agents working in this repository.

## Project Overview

**Playwright MCP Server** - A Model Context Protocol (MCP) server that provides browser automation capabilities using Playwright. Exposes tools for navigation, interaction, extraction, screenshots, multi-page management, and JavaScript evaluation.

- **Package**: `playwright-mcp-server` (version 0.2.0)
- **Python**: >=3.10
- **Key dependencies**: `mcp>=2.0.0`, `playwright>=1.50.0`, `pydantic>=2.0.0`

## Essential Commands

| Task | Command |
|------|---------|
| Install (editable) | `pip install -e .` |
| Install with dev deps | `pip install -e ".[dev]"` |
| Install Playwright browsers | `playwright install chromium` |
| Run server (stdio) | `playwright-mcp` |
| Run server (headed) | `playwright-mcp --headed` |
| Run server (Firefox) | `playwright-mcp --browser firefox` |
| Run tests (unit only) | `pytest -m "not integration"` |
| Run integration tests | `pytest -m integration` |
| Run all tests | `pytest` |
| Type checking | `mypy playwright_mcp` |
| Linting | `ruff check playwright_mcp` |
| Formatting | `ruff format playwright_mcp` |

### CLI Options
```
--headless / --headed          # Headless mode (default: True)
--browser {chromium,firefox,webkit}  # Browser engine
--timeout FLOAT                # Default timeout in ms
--slow-mo FLOAT                # Slow down operations by ms
--browser-arg STR              # Additional browser launch args (repeatable)
--log-level {DEBUG,INFO,WARNING,ERROR}
```

## Architecture

```
playwright_mcp/
├── __init__.py      # Package exports, version
├── __main__.py      # Entry point (asyncio.run(main()))
├── cli.py           # CLI argument parsing & config building
├── config.py        # Frozen dataclasses: BrowserConfig, ServerConfig
├── browser.py       # BrowserManager - lifecycle & page pool
├── tools.py         # MCP Tool definitions (schema only)
├── executor.py      # ToolExecutor - actual Playwright operations
├── handlers.py      # RequestHandlers - MCP protocol handlers
└── server.py        # PlaywrightMCPServer - main server class
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `config.py` | Immutable configuration dataclasses with defaults |
| `browser.py` | BrowserManager - manages Playwright lifecycle, page pool, locking |
| `tools.py` | Static MCP Tool schemas (16 tools) |
| `executor.py` | ToolExecutor - executes tools against BrowserManager |
| `handlers.py` | RequestHandlers - MCP request handlers (tools, resources) |
| `server.py` | PlaywrightMCPServer - wires components, manages stdio transport |
| `cli.py` | Parses args, builds config, runs server |
| `__main__.py` | Thin entry point delegating to server.main() |

## Data Flow

```
Client (MCP) → handlers.RequestHandlers → executor.ToolExecutor → browser.BrowserManager → Playwright
                ↑
                └── Returns: types.CallToolResult / types.ListToolsResult / types.ReadResourceResult
```

1. **MCP Request** arrives at `RequestHandlers`
2. **Handlers** ensure browser initialized, delegate to `ToolExecutor`
3. **Executor** dispatches to `_handle_{tool_name}` method
4. **Executor** gets `Page` from `BrowserManager.get_page()`
5. **Executor** performs Playwright operation, returns `CallToolResult`
6. **BrowserManager** manages browser/context/pages with async lock

## Key Patterns & Conventions

### Configuration
- Uses **frozen dataclasses** (`@dataclass(frozen=True)`) for immutability
- `DEFAULT_CONFIG = ServerConfig()` as module-level singleton
- Factory functions: `create_browser_manager()`, `create_server()`

### BrowserManager
- **Single browser instance** with **single context** (created on `initialize()`)
- **Page pool**: `dict[str, Page]` with `current_page_id` for default
- **Async lock** (`asyncio.Lock`) protects initialization/cleanup
- **Lifespan context manager** for proper cleanup: `async with manager.lifespan():`
- Pages are **not closed individually** - context cleanup handles it

### ToolExecutor
- Dynamic dispatch: `getattr(self, f"_handle_{name}")`
- All handlers return `types.CallToolResult`
- Errors caught and returned as error results (not raised)
- Uses `default_timeout` from config (30000ms default)

### RequestHandlers
- Registers with MCP `Server` via `register()` method
- Handles: `tools/list`, `tools/call`, `resources/list`, `resources/read`, `resources/templates/list`
- Resources: screenshot URIs `screenshot://{page_id}` return base64 PNG

### Async Patterns
- All public methods are `async`
- Uses `asynccontextmanager` for lifespan management
- `asyncio.run()` only at entry points (`__main__.py`, `cli.py`)

## Testing

### Structure
- `tests/test_unit.py` - Unit tests (no browser needed)
- `tests/test_integration.py` - Integration tests (requires browser, marked `@pytest.mark.integration`)
- `tests/conftest.py` - Pytest config: integration marker, session-scoped event loop

### Running Tests
```bash
pytest                    # All tests
pytest -m "not integration"  # Unit only (fast)
pytest -m integration   # Integration only (slow, needs playwright install)
```

### Test Patterns
- Unit tests: instantiate classes directly, mock where needed
- Integration tests: use `async with manager.lifespan():` for lifecycle
- TestExecutor tests verify `result.is_error` and content types

## Gotchas & Non-Obvious Details

### Browser Initialization
- **Lazy initialization**: Browser starts on first tool call via `handlers.handle_call_tool()` calling `await self._browser.initialize()`
- **Not thread-safe**: Single `BrowserManager` instance, protected by async lock only
- **Context not recreated**: Single context for all pages - cookies/storage shared

### Page Management
- Default page ID is `"default"` (created on `initialize()`)
- `remove_page()` **does not close the page** - only removes from pool
- Switching pages updates `current_page_id` but doesn't bring to front

### Tool Execution
- All tools accept optional `page_id` parameter (defaults to current page)
- `click` uses `page.click()` (not `locator().click()`)
- `type` uses `page.fill()` (not `type()` - fills entire input)
- Screenshots return `ImageContent` with base64 PNG data
- `evaluate` returns JSON-stringified result via `json.dumps(result, default=str)`

### Resource Handling
- `resources/list` returns screenshot resources for **all pages**
- `resources/read` takes `screenshot://{page_id}` URI
- No resource templates implemented (returns empty list)

### CLI Config Building
- `--headless` and `--headed` are mutually exclusive flags on same dest
- If only `--browser-arg`/`--slow-mo` given (no `--headless`), uses defaults for other browser config
- Config building logic in `cli.build_config()` is somewhat complex - test after changes

### Logging
- Uses standard `logging` module
- Logger names: `__name__` per module
- CLI sets up `basicConfig` with format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`

### Type Safety
- `pyproject.toml` enforces strict mypy: `disallow_untyped_defs = true`, `warn_return_any = true`
- All public functions have type hints
- Uses `from __future__ import annotations` for forward references

### Error Handling
- ToolExecutor catches **all exceptions** (`except Exception`) and returns error result
- Errors include string representation in `TextContent`
- No structured error codes - clients parse error text

## Adding New Tools

1. Add schema to `tools.py:TOOLS` list (follow existing pattern)
2. Add `_handle_{name}` method to `ToolExecutor` in `executor.py`
3. Method signature: `async def _handle_{name}(self, args: dict[str, Any]) -> types.CallToolResult`
4. Use `self._get_page(args.get("page_id"))` for page access
5. Return `types.CallToolResult(content=[...], is_error=bool)`

## Extending Resources

1. Add URI scheme handling in `handlers.py:handle_read_resource`
2. Add resource listing in `handlers.py:handle_list_resources`
3. Consider adding resource templates if needed

## Common Tasks

### Run Server for Development
```bash
pip install -e ".[dev]"
playwright install chromium
playwright-mcp --headed --log-level DEBUG
```

### Debug Tool Execution
```python
from playwright_mcp import create_server, ServerConfig, BrowserConfig
from playwright_mcp.executor import ToolExecutor

config = ServerConfig(browser=BrowserConfig(headless=True))
server = create_server(config)
async with server.lifespan():
    executor = ToolExecutor(server.browser)
    result = await executor.execute("navigate", {"url": "https://example.com"})
    print(result)
```

### Add Browser Argument
```bash
playwright-mcp --browser-arg "--disable-web-security" --browser-arg "--no-sandbox"
```

## File Modification Impact

| File | Impact |
|------|--------|
| `config.py` | Affects all components - changes propagate everywhere |
| `browser.py` | Core lifecycle - impacts initialization, page management, cleanup |
| `tools.py` | Only adds tool definitions - no logic |
| `executor.py` | Tool implementation - direct Playwright interaction |
| `handlers.py` | MCP protocol - request/response handling |
| `server.py` | Wiring - server creation, lifespan, stdio transport |
| `cli.py` | CLI only - argument parsing, config building |

## Version & Release

- Version in `pyproject.toml` and `playwright_mcp/__init__.py` (must match)
- `cli.py` version in `ArgumentParser` version string
- Build: `pip install -e .` creates `playwright-mcp` entry point