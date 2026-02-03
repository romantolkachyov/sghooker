# AGENTS.md

## Build, Lint, Test
- **Build**: `uv sync`
- **Format**: `uv run ruff format --check`
- **Lint**: `uv run ruff check .`
- **Type‑check**: `uv run mypy .`
- **Run all tests**: `uv run pytest tests`
- **Run a single test**: `uv run pytest tests/<test_file>.py::<test_name> -v`

## Code Style Guidelines
### Imports
```python
# Standard library
import json
import logging

# Third‑party
import httpx
import msgspec

# Local
from sghooker.containers import Container
from sghooker.schemas import AlertEvent
```
- Keep imports sorted and grouped.
- Use explicit imports; avoid `from x import *`.

### Formatting
- Run `ruff format`; line length ~120.
- `snake_case` for variables/functions, `PascalCase` for classes.

### Types & Validation
- Use `msgspec` or `typing` for public APIs.
- Validate payloads with `msgspec.Struct` and `tag`/`tag_field`.
- Return typed models from builders.

### Error Handling
- Catch specific exceptions; log with structured message.
- Do not swallow errors; propagate unrecoverable ones.
- Return consistent error JSON with `status_code` and `detail`.

### Logging
- Use `logging`; include request ID when available.

### Naming Conventions
- Functions: `build_<event>_message`, `send_<service>_message`.
- Classes: `AlertEventMessage`, `IssueCreatedCard`.
- Files: one public class/function per file; name matches identifier.

### Testing
- Use `pytest` with `pytest‑asyncio`.
- Mock with `unittest.mock.AsyncMock`.
- Fixtures in `tests/conftest.py`.
- Test files under `tests/`; pattern `test_*.py`.

## Project Structure
```
/sghooker
├─ main.py               # FastAPI app, webhook endpoint
├─ containers.py         # DI container
├─ google_chat.py        # Async client for Chat webhook
├─ chat_messages.py      # Card builder functions
└─ schemas/
    ├─ __init__.py
    ├─ alert_event.py
    └─ issue_event.py
└─ tests/
    ├─ conftest.py
    ├─ test_webhook.py
    └─ test_messages.py
```

## Key Entities & Responsibility
- **main.py**: FastAPI entry point; handles incoming webhook, routes to handlers.
- **containers.py**: Dependency‑injector container; provides app config, services.
- **google_chat.py**: Async client; posts cards to Google Chat webhook URLs.
- **chat_messages.py**: Functions that build `Message` objects from events.
- **schemas/**: `msgspec` models for webhook payloads; tagged unions for event types.
- **tests/**: Unit and integration tests; use `pytest‑asyncio` for async code.
