"""CLI for sending test messages to Google Chat."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Annotated, Any

import msgspec
import typer

from sghooker.chat_messages import (
    build_alert_event_message,
    build_issue_created_message,
    build_issue_unresolved_message,
)
from sghooker.google_chat import send_message
from sghooker.schemas.alert_event import AlertEventWebhookBody
from sghooker.schemas.issue_event import IssueCreatedWebhookBody, IssueUnresolvedWebhookBody

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="CLI for sending test messages to Google Chat")


def _load_env_config() -> dict[str, str | None]:
    """Load configuration from environment variables."""
    return {
        "webhook_url": os.getenv("WEBHOOK_URL"),
        "grafana_url_template": os.getenv("GRAFANA_URL_TEMPLATE"),
        "tracing_url_template": os.getenv("TRACING_URL_TEMPLATE"),
    }


def _validate_config(config: dict[str, str | None]) -> None:
    """Validate that required configuration is present."""
    if not config["webhook_url"]:
        typer.echo("Error: WEBHOOK_URL environment variable is required", err=True)
        raise typer.Exit(code=1)


def _load_json_file(file_path: Path) -> dict[str, Any]:
    """Load and parse JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        typer.echo(f"Error: File not found: {file_path}", err=True)
        raise typer.Exit(code=1)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Invalid JSON in file {file_path}: {e}", err=True)
        raise typer.Exit(code=1)


def _detect_event_type(data: dict[str, Any]) -> str:
    """Detect the event type from the JSON data."""
    # Check for alert event
    if "event" in data and "title" in data.get("event", {}):
        if "alert_rule" in data:
            return "alert_event"

    # Check for issue events
    if "data" in data:
        action = data.get("action", "").lower()
        if action == "created":
            return "issue_created"
        elif action == "unresolved":
            return "issue_unresolved"

    # Default to alert event if we can't detect
    typer.echo("Warning: Could not detect event type, defaulting to alert_event", err=True)
    return "alert_event"


def _parse_event_data(event_type: str, data: dict[str, Any]) -> msgspec.Struct:
    """Parse the JSON data into the appropriate schema."""
    try:
        if event_type == "alert_event":
            return msgspec.convert(data, type=AlertEventWebhookBody)
        elif event_type == "issue_created":
            return msgspec.convert(data, type=IssueCreatedWebhookBody)
        elif event_type == "issue_unresolved":
            return msgspec.convert(data, type=IssueUnresolvedWebhookBody)
        else:
            typer.echo(f"Error: Unknown event type: {event_type}", err=True)
            raise typer.Exit(code=1)
    except msgspec.ValidationError as e:
        typer.echo(f"Error: JSON validation failed: {e}", err=True)
        raise typer.Exit(code=1)


async def _send_message_async(
    event_data: msgspec.Struct,
    event_type: str,
    grafana_url_template: str | None,
    tracing_url_template: str | None,
) -> None:
    """Send message to Google Chat asynchronously."""
    # Build message based on event type
    if event_type == "alert_event":
        message = build_alert_event_message(
            event_data,  # type: ignore[arg-type]
            grafana_url_template=grafana_url_template,
            tracing_url_template=tracing_url_template,
        )
    elif event_type == "issue_created":
        message = build_issue_created_message(event_data)  # type: ignore[arg-type]
    elif event_type == "issue_unresolved":
        message = build_issue_unresolved_message(event_data)  # type: ignore[arg-type]
    else:
        typer.echo(f"Error: Unknown event type: {event_type}", err=True)
        raise typer.Exit(code=1)

    # Send the message
    await send_message(dict(message.render()))


@app.command(name="send-test-message")
def send_test_message(
    file_path: Annotated[
        Path,
        typer.Argument(
            ...,
            help="Path to JSON file containing the webhook payload",
            exists=True,
            readable=True,
        ),
    ],
    event_type: Annotated[
        str | None,
        typer.Option(
            "--event-type",
            "-t",
            help="Event type (alert_event, issue_created, issue_unresolved). Auto-detected if not specified.",
        ),
    ] = None,
) -> None:
    """Send a test message to Google Chat from a JSON file.

    The command reads a JSON file containing a webhook payload, validates it against
    the appropriate schema, builds a Google Chat message, and sends it to the webhook
    URL configured via the WEBHOOK_URL environment variable.

    Examples:
        export WEBHOOK_URL="https://chat.googleapis.com/v1/spaces/..."
        sghooker send-test-message payload.json
        sghooker send-test-message payload.json --event-type alert_event
    """
    # Load and validate configuration
    config = _load_env_config()
    _validate_config(config)

    # Load JSON file
    typer.echo(f"Loading JSON file: {file_path}")
    data = _load_json_file(file_path)

    # Detect or use provided event type
    detected_event_type = event_type or _detect_event_type(data)
    typer.echo(f"Event type: {detected_event_type}")

    # Parse and validate the event data
    typer.echo("Validating JSON payload...")
    event_data_obj = _parse_event_data(detected_event_type, data)

    # Send the message
    typer.echo("Sending message to Google Chat...")
    asyncio.run(
        _send_message_async(
            event_data_obj,
            detected_event_type,
            config["grafana_url_template"],
            config["tracing_url_template"],
        )
    )

    typer.echo("Message sent successfully!")


@app.command(name="validate")
def validate_payload(
    file_path: Annotated[
        Path,
        typer.Argument(
            ...,
            help="Path to JSON file containing the webhook payload",
            exists=True,
            readable=True,
        ),
    ],
    event_type: Annotated[
        str | None,
        typer.Option(
            "--event-type",
            "-t",
            help="Event type (alert_event, issue_created, issue_unresolved). Auto-detected if not specified.",
        ),
    ] = None,
) -> None:
    """Validate a JSON payload file without sending it.

    This command validates that the JSON file matches the expected schema
    for the given event type.

    Examples:
        sghooker validate payload.json
        sghooker validate payload.json --event-type issue_created
    """
    # Load JSON file
    typer.echo(f"Loading JSON file: {file_path}")
    data = _load_json_file(file_path)

    # Detect or use provided event type
    detected_event_type = event_type or _detect_event_type(data)
    typer.echo(f"Event type: {detected_event_type}")

    # Parse and validate the event data
    typer.echo("Validating JSON payload...")
    _parse_event_data(detected_event_type, data)

    typer.echo("Validation successful!")


if __name__ == "__main__":
    app()
