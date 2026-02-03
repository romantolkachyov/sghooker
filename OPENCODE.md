# OpenCode Tool Usage Guide

## General
- Every tool call must follow its JSON schema.
- Provide a `description` for actions that modify state or require context.

## Bash
- Required: `command` (the shell command) and `description` (brief purpose).
- Do not use `cd`; use `workdir` if you need to change directory.
- Boolean options (e.g., `replaceAll`) must be `true`/`false` without quotes.

## Read / Write
- `read`: only `filePath` is required.
- `write`: requires `filePath` and `content`. Ensure content is a valid string.

## Edit
- Provide `filePath`, `oldString`, `newString`.
- `replaceAll` must be a boolean (`true`/`false`), not a quoted string.

## Glob / Grep
- `glob`: `pattern` is required; optionally `path`.
- `grep`: `pattern` is required; optionally `path` and `include`.

## Best Practice
- Test tool arguments in a sandbox call before executing.
- Verify output before proceeding to next step.
- Keep responses concise; avoid extra fields.
