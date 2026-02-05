# AGENTS.md

## Pre-Commit Hooks and Workflow
- **Pre-commit Checks**: After making changes, run `uv pre-commit run --all-files` to ensure all hooks pass (formatting, linting, type-checking).
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
import logging
from typing import Annotated

# Third-party
import httpx
import msgspec
from pulya import Pulya
from dependency_injector import containers

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
- Prefer static typing; use type hints for all function parameters and return values.
- Enable `strict = true` in mypy configuration.

### Error Handling
- Catch specific exceptions rather than broad ones (e.g., `Exception`).
- Log errors with structured messages using the `logging` module.
- Do not swallow errors; propagate unrecoverable ones to the caller.
- Return consistent error JSON with `status_code` and `detail`.

### Logging
- Use Python's built-in `logging` module for all log output.
- Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- Include context in logs when processing webhook events.

### Naming Conventions
- **Functions**: Use prefixes like `build_<event>_message` or `send_<service>_message`.
- **Classes**: Use `PascalCase`, e.g., `AlertEventMessage`, `IssueCreatedCard`.
- **Variables/Constants**: Use `snake_case`, e.g., `max_retries = 3`.
- **Files**: One public class or function per file; filename should match the identifier.

### Testing
- Use `pytest` with `pytest-asyncio` for async code testing.
- Mock dependencies using `unittest.mock.AsyncMock`.
- Use `polyfactory` with `MsgspecFactory` for generating test data.
- Test files follow the pattern `*_test.py` and are located in `tests/`.
- Define reusable fixtures in `tests/conftest.py`.

## Project Structure
```
/sghooker
├─ main.py               # Pulya app, webhook endpoint
├─ containers.py         # DI container using dependency-injector
├─ google_chat.py        # Async client for Google Chat webhook URLs
├─ chat_messages.py      # Card builder functions
└─ schemas/
    ├─ __init__.py       # Exports public schema models
    ├─ alert_event.py    # Defines `AlertEvent` model variants
    └─ issue_event.py    # Defines `IssueEvent` model variants
└─ tests/
    ├─ conftest.py       # Pytest fixtures
    ├─ build_messages_test.py
    └─ *_test.py         # Test files
```

## Key Entities & Responsibility
- **main.py**: Pulya entry point; handles incoming webhooks using dependency injection.
- **containers.py**: DI container using `dependency-injector` library.
- **google_chat.py**: Async client for posting cards to Google Chat webhook URLs.
- **chat_messages.py**: Functions that build `Message` objects from event payloads.
- **schemas/**: Defines `msgspec` models for webhook payloads using tagged unions.
- **tests/**: Unit tests using `pytest` and `polyfactory` for test data generation.

## Agent Instructions
1. **Pre-Commit Hooks**: Always run `uv pre-commit run --all-files` after making changes.
2. **Todo List Management**: Use `todowrite` tool to organize work into actionable items.
3. **Code Generation**: Adhere to style guidelines; avoid code that could be used maliciously.
4. **Testing**: Write tests for new features using `pytest` and `polyfactory`.
5. **Error Handling**: Use specific exceptions and structured logging.
6. **Documentation**: Add docstrings to public APIs using Google-style format.

## Cursor Rules (if any)
- No specific Cursor rules were found in `.cursor/rules/` or `.cursorrules/`.

## Copilot Instructions (if any)
- No specific Copilot instructions were found in `.github/copilot-instructions.md`.

## Security Guidelines
1. **Secrets Management**: Never log secrets; use environment variables.
2. **Input Validation**: Validate all incoming payloads using `msgspec`.
3. **Dependency Safety**: Regularly update dependencies (`uv sync`).
4. **Error Messages**: Avoid exposing internal details in error messages.

## Example Workflow for Agents
1. **Analyze Requirements**: Understand the task.
2. **Create Todo List**: Break down the task using `todowrite`.
3. **Generate Code**: Write code adhering to style guidelines.
4. **Write Tests**: Add tests using `pytest` and `polyfactory`.
5. **Run Checks**: Execute `uv pre-commit run --all-files`.
6. **Commit Changes**: Commit with a clear message.

For help with opencode, use `/help`. To report issues, visit [https://github.com/anomalyco/opencode/issues](https://github.com/anomalyco/opencode/issues).
