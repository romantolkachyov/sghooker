# AGENTS.md

## Pre-Commit Hooks and Workflow
- **Pre-commit Checks**: After making changes, run `uv pre-commit run --all-files` to ensure all pre-commit hooks pass (e.g., formatting, linting, type-checking).
  - This step is critical before committing or pushing changes.

## Build, Lint, Test
- **Build**: `uv sync`
  - Synchronizes dependencies using UV.
- **Format**: `uv run ruff format --check`
  - Checks code formatting compliance with Ruff.
- **Lint**: `uv run ruff check .`
  - Runs Ruff linter on the entire project.
- **Type-check**: `uv run mypy .`
  - Validates type correctness using mypy.
- **Run all tests**: `uv run pytest tests`
  - Executes all test cases in the `tests/` directory.
- **Run a single test**: `uv run pytest tests/<test_file>.py::<test_name> -v`
  - Runs a specific test case with verbose output for debugging.

## Code Style Guidelines
### Imports
```python
# Standard library
import json
import logging

# Third-party
import httpx
import msgspec

# Local
from sghooker.containers import Container
from sghooker.schemas import AlertEvent
```
- Keep imports sorted and grouped by category (standard, third-party, local).
- Use explicit imports; avoid `from x import *`.
- Ensure all imported modules are used in the file.

### Formatting
- Run `ruff format` to enforce consistent code formatting.
- Line length should not exceed 120 characters.
- Use `snake_case` for variables and functions, `PascalCase` for classes.
- Avoid trailing whitespace; ensure no mixed indentation (use spaces only).

### Types & Validation
- Use `msgspec` or `typing` for public APIs to define typed models.
- Validate payloads using `msgspec.Struct`, `tag`, and `tag_field`.
- Return strongly-typed models from builder functions.
- Prefer static typing where possible; use type hints for function parameters and return values.

### Error Handling
- Catch specific exceptions rather than broad ones (e.g., `Exception`).
- Log errors with structured messages using the `logging` module.
  - Include request IDs when available for traceability.
- Do not swallow errors; propagate unrecoverable ones to the caller.
- Return consistent error JSON with `status_code` and `detail`.

### Logging
- Use Python's built-in `logging` module for all log output.
- Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- Include request IDs in logs when processing webhook events or API requests.
  - Format: `[<request_id>] <log_message>`

### Naming Conventions
- **Functions**: Use prefixes like `build_<event>_message` or `send_<service>_message`.
- **Classes**: Use `PascalCase`, e.g., `AlertEventMessage`, `IssueCreatedCard`.
- **Variables/Constants**: Use `snake_case`, e.g., `max_retries = 3`.
- **Files**: One public class or function per file; filename should match the identifier (e.g., `chat_messages.py` for `chat_messages` module).

### Testing
- Use `pytest` with `pytest-asyncio` for async code testing.
- Mock dependencies using `unittest.mock.AsyncMock`.
- Define fixtures in `tests/conftest.py` for reusable test setup/teardown.
- Test files should follow the pattern `test_*.py` and be located in `tests/`.

## Project Structure
```
/sghooker
├─ main.py               # FastAPI app, webhook endpoint
├─ containers.py         # DI container; provides app config, services
├─ google_chat.py        # Async client for Google Chat webhook URLs
├─ chat_messages.py      # Card builder functions (e.g., `build_alert_message`)
└─ schemas/
    ├─ __init__.py         # Exports public schema models
    ├─ alert_event.py       # Defines `AlertEvent` model and variants
    └─ issue_event.py       # Defines `IssueEvent` model and variants
└─ tests/
    ├─ conftest.py          # Pytest fixtures (e.g., async client, mock services)
    ├─ test_webhook.py      # Tests for webhook endpoint and handlers
    └─ test_messages.py     # Tests for message builders in `chat_messages.py`
```

## Key Entities & Responsibility
- **main.py**: FastAPI entry point; handles incoming webhooks, routes to appropriate handlers.
- **containers.py**: Dependency injection container; provides app configuration and service instances.
- **google_chat.py**: Async client for posting cards to Google Chat webhook URLs.
  - Should implement retry logic for transient failures.
- **chat_messages.py**: Functions that build `Message` objects from event payloads.
  - Follow naming conventions like `build_<event>_card`.
- **schemas/**: Defines `msgspec` models for webhook payloads using tagged unions for event types.
  - Use `tag` and `tag_field` for discriminated unions.
- **tests/**: Unit and integration tests; use `pytest-asyncio` for async code.

## Agent Instructions
1. **Pre-Commit Hooks**:
   - Always run `uv pre-commit run --all-files` after making changes to ensure all hooks pass.
2. **Todo List Management**:
   - At the start of a task, create a todo list using the `todowrite` tool to organize work into actionable items.
   - Ensure each item is small and can be completed independently.
   - Use the todo list to track progress and maintain context across the workflow.
   - After completing an item, mark it as `completed`.
3. **Code Generation**:
   - Generate code that adheres to the style guidelines above.
   - Avoid generating code that could be used maliciously (e.g., no shell command execution, no file deletion).
4. **Testing**:
   - Write tests for new features or fixes using `pytest` and `unittest.mock`.
   - Ensure test files follow the naming convention (`test_*.py`).
5. **Error Handling**:
   - Implement robust error handling with specific exceptions and structured logging.
6. **Logging**:
   - Include request IDs in logs for traceability.
7. **Naming**:
   - Follow naming conventions for functions, classes, and variables.
8. **Documentation**:
   - Add docstrings to public APIs (functions, classes) using Google-style format.

## Cursor Rules (if any)
- No specific Cursor rules were found in `.cursor/rules/` or `.cursorrules/`.
  - If added later, ensure they align with the code style guidelines above.

## Copilot Instructions (if any)
- No specific Copilot instructions were found in `.github/copilot-instructions.md`.
  - If added later, ensure they align with the code style and security guidelines.

## Security Guidelines
1. **Secrets Management**:
   - Never log secrets or sensitive data (e.g., API keys, tokens).
   - Use environment variables for configuration (e.g., `os.getenv('GOOGLE_CHAT_WEBHOOK_URL')`).
2. **Input Validation**:
   - Validate all incoming payloads using `msgspec` or Pydantic.
3. **Dependency Safety**:
   - Regularly update dependencies (`uv sync`).
4. **Error Messages**:
   - Avoid exposing internal details in error messages to users.

## Example Workflow for Agents
1. **Analyze Requirements**: Understand the task (e.g., add a new feature, fix a bug).
2. **Create Todo List**: Use `todowrite` to break down the task into small, actionable items.
   - Each item should be independent and testable.
3. **Generate Code**: Write code adhering to style and security guidelines.
4. **Write Tests**: Add tests for the new functionality using `pytest`.
5. **Run Checks**: After completing an item, run:
   - `uv pre-commit run --all-files` (formatting, linting, type-checking).
   - `uv run pytest tests/<test_file>.py::<test_name> -v` (specific test).
6. **Commit Changes**: If all checks pass, commit the changes with a clear message.
7. **Log Changes**: Document changes in a concise commit message (e.g., "Add support for issue comment events").

For help with opencode, use `/help`. To report issues, visit [https://github.com/anomalyco/opencode/issues](https://github.com/anomalyco/opencode/issues).
