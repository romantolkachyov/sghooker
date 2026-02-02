# sghooker Agent Guide

## Project Overview

**sghooker** is a Python ASGI webservice that consumes Sentry webhooks and forwards them to Google Chat with rich card formatting. The service monitors error alerts and issue notifications from Sentry and displays them in Google Chat spaces using interactive cards.

**Tech Stack:**
- Python 3.12+ (ASGI async application)
- Granian (ASGI server) with uvloop
- Pulya (ASGI framework with dependency injection)
- msgspec (high-performance schema validation)
- python-card-framework (Google Chat cards)
- dependency-injector (DI container)
- pytest + pytest-asyncio (testing)
- ruff + mypy (linting & type checking)
- uv (package manager)

## Architecture Overview

The application follows a simple request flow:

```
Sentry Webhook → Pulya Endpoint → Message Builder → Google Chat API
```

### Key Components:

1. **Webhook Handler** (`main.py:receive_webhook`) - Main ASGI endpoint accepting Sentry webhooks via POST to `/inbox/sentry/`
2. **Dependency Injection** (`containers.py`) - Request-scoped DI container using dependency-injector
3. **Message Builders** (`chat_messages.py`) - Functions to build Google Chat cards from webhook data
4. **Schema Validation** (`schemas/`) - msgspec tagged unions for typed parsing of webhook payloads
5. **Google Chat Client** (`google_chat.py`) - Async HTTP client for sending messages

### Supported Webhook Events:

- **Alert Event (triggered)** - Issue alert triggered (schemas/alert_event.py:43)
- **Issue Created** - New issue created (schemas/issue_event.py:41)
- **Issue Resolved** - Issue resolved (schemas/issue_event.py:45)
- **Issue Unresolved** - Issue reopened (schemas/issue_event.py:53)

## Codebase Structure

```
sghooker/
├── __init__.py
├── main.py              # FastAPI app with webhook endpoints
├── containers.py        # DI container configuration
├── google_chat.py       # Google Chat API client
├── chat_messages.py     # Message builders (alert, issue events)
└── schemas/
    ├── __init__.py
    ├── alert_event.py   # Alert event schemas
    └── issue_event.py   # Issue event schemas
```

### Key Files:

- **main.py** - ASGI application with endpoints: `/inbox/sentry/` (POST), `/`, `/healthcheck`, `/readiness`
- **containers.py** - DI container with request-scoped headers provider
- **google_chat.py** - `send_message()` function requiring `WEBHOOK_URL` env var
- **chat_messages.py** - Message building functions using card_framework v2
- **schemas/alert_event.py** - Alert event with stacktrace and exception data
- **schemas/issue_event.py** - Issue lifecycle events with project metadata

## Development Commands

```bash
# Install dependencies
uv sync

# Run development server (granian)
uv run granian --interface rsgi --host 0.0.0.0 --port 8000 sghooker.main:app

# Run linters
uv run ruff format --check
uv run mypy

# Run tests
uv run pytest tests

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Code Quality Tools:

- **ruff** - Linting and formatting (configured in pyproject.toml)
- **mypy** - Strict type checking (pyproject.toml:24)
- **pre-commit** - Hooks for linting, formatting, mypy, and lock file consistency

## Adding New Features

### Adding New Webhook Event Types:

1. **Create schema** in appropriate `schemas/` file using msgspec.Struct with tag
2. **Add to union** in main.py:24 (WebHookBodyUnion)
3. **Create message builder** in chat_messages.py returning card_framework.Message
4. **Handle in endpoint** in main.py:receive_webhook (elif branch)

Example pattern:
```python
# schemas/new_event.py
class NewEventData(msgspec.Struct):
    field: str

class NewEventWebhookBody(msgspec.Struct, tag="new_action", tag_field="action"):
    data: NewEventData

# main.py
from sghooker.schemas.new_event import NewEventWebhookBody

WebHookBodyUnion = (
    ... | NewEventWebhookBody | None
)

@inject
async def receive_webhook(...):
    if isinstance(body, NewEventWebhookBody):
        result = build_new_event_message(body)
        await send_message(dict(result.render()))
```

### Modifying Google Chat Cards:

Use card_framework v2 components from chat_messages.py:
- `CardWithId` - Main card container
- `CardHeader` - Card title, subtitle, image
- `Section` - Grouped widgets
- `Widget` - TextParagraph, DecoratedText, ButtonList, ChipList
- `Button` - Action buttons with OnClick handlers

## Testing Guidelines

### Test Structure:

- **tests/example_test.py** - Endpoint integration tests using pulya.testing.TestClient
- **tests/build_messages_test.py** - Message builder tests using polyfactory
- **tests/mocks/** - Sample webhook payloads from Sentry

### Testing Patterns:

```python
# Endpoint testing
from pulya.testing import TestClient
import pytest

@pytest.fixture
async def client():
    async with TestClient(app) as client:
        yield client

async def test_endpoint(client: TestClient):
    r = await client.post("/inbox/sentry/", content=mock_data)
    assert r.status_code == 200
```

```python
# Message builder testing
from polyfactory.factories.msgspec_factory import MsgspecFactory

class AlertEventWebhookBodyFactory(MsgspecFactory[AlertEventWebhookBody]): ...

def test_build_message():
    result = build_alert_event_message(AlertEventWebhookBodyFactory.build())
    assert result.cards_v2[0].header.title
```

Run tests: `pytest tests -v`

## Deployment

### Docker Deployment:

Multi-stage Dockerfile using Wolfi Python 3.13 base:
1. **Builder stage** - Install dependencies with uv
2. **Runtime stage** - Copy venv and run Granian

Build and run:
```bash
docker build -t sghooker .
docker run -p 8000:8000 -e WEBHOOK_URL=https://... sghooker
```

### Environment Variables:

- `WEBHOOK_URL` (required) - Google Chat webhook URL for sending messages

### Server Entry:

Granian server with RSGI interface (Dockerfile:29):
```
granian --interface rsgi --host 0.0.0.0 --port 8000 sghooker.main:app
```

## CI/CD Pipeline

### GitHub Actions:

- **build.yml** - Runs on push to master and PRs: ruff format, mypy, pytest
- **docker.yml** - Builds and pushes to Docker Hub on tags (v*)

### Pre-commit Hooks:

Enabled hooks (.pre-commit-config.yaml):
- ruff-check, ruff-format
- mypy (strict)
- toml-sort-fix
- uv-lock
- Various sanity checks (JSON, YAML, etc.)

Run manually: `pre-commit run --all-files`

## Common Tasks

### Adding New Sentry Webhook Types:

1. Export sample payload from Sentry webhook configuration
2. Create msgspec schema matching the payload structure
3. Use tag field for union discrimination (e.g., `tag_field="action"`)
4. Add to WebHookBodyUnion in main.py
5. Create message builder function in chat_messages.py
6. Add handler branch in receive_webhook()

### Modifying Google Chat Card Formatting:

Edit functions in chat_messages.py:
- `build_alert_event_message()` - Alert triggered events
- `build_issue_created_message()` - Issue created events
- `build_issue_unresolved_message()` - Issue reopened events

Common modifications:
- Add/remove widgets from sections
- Change header styling
- Add custom buttons with OpenLink
- Add ChipList for tags

### Debugging Webhook Payloads:

Check logs for unsupported body types. Use mock files in tests/mocks/ for testing:
```python
import msgspec.json
with open("tests/mocks/alert_triggered.json") as fp:
    data = msgspec.json.decode(fp.read(), type=AlertEventWebhookBody)
```

## Important Notes

- **Type Safety**: All code passes mypy strict mode
- **Async Everything**: All I/O operations are async (httpx, granian)
- **Dependency Injection**: Use @inject decorator for dependencies from containers
- **No Secrets in Code**: WEBHOOK_URL is environment variable only
- **Docker Multi-platform**: Supports linux/amd64 and linux/arm64
