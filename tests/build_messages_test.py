"""Tests for chat message builders."""

from pathlib import Path

import msgspec.json
from anyio import open_file
from polyfactory.factories.msgspec_factory import MsgspecFactory

from sghooker.chat_messages import (
    build_alert_event_message,
    build_issue_created_message,
    build_issue_unresolved_message,
)
from sghooker.schemas.alert_event import AlertEventWebhookBody
from sghooker.schemas.issue_event import (
    IssueCreatedWebhookBody,
    IssueResolvedWebhookBody,
    IssueUnresolvedWebhookBody,
)

MOCKS_DIR = Path(__file__).parent / "mocks"


class AlertEventWebhookBodyFactory(MsgspecFactory[AlertEventWebhookBody]):
    """Factory for generating AlertEventWebhookBody test data."""


class IssueCreatedWebhookBodyFactory(MsgspecFactory[IssueCreatedWebhookBody]):
    """Factory for generating IssueCreatedWebhookBody test data."""


def test_build_alert_event_message() -> None:
    """Test building a message from an alert event."""
    result = build_alert_event_message(AlertEventWebhookBodyFactory.build())
    _ = result.render()


def test_build_alert_event_message_from_example() -> None:
    """Test building a message from an example alert event JSON file."""
    with Path.open(MOCKS_DIR / "alert_triggered.json") as fp:
        msg = msgspec.json.decode(fp.read(), type=AlertEventWebhookBody)
    result = build_alert_event_message(msg)
    _ = result.render()


def test_build_alert_event_message_with_grafana_url() -> None:
    """Test building a message with a Grafana URL template."""
    with Path.open(MOCKS_DIR / "alert_triggered.json") as fp:
        msg = msgspec.json.decode(fp.read(), type=AlertEventWebhookBody)
    # Add required tags to the mock data if they are missing
    msg.data.event.tags.append(("namespace", "my-ns"))
    msg.data.event.tags.append(("service_name", "my-svc"))

    template = 'https://grafana.example.com/explore?left=["now-1h","now","Loki",{"expr":"{{namespace=\'{namespace}\',service_name=\'{service_name}\'}}"}]'
    result = build_alert_event_message(msg, grafana_url_template=template)
    rendered = result.render()

    # Find the Logs button in the rendered card
    buttons = rendered["cardsV2"][0]["card"]["sections"][-1]["widgets"][0]["buttonList"]["buttons"]
    logs_button = next(b for b in buttons if b["text"] == "Logs")
    expected_url = template.replace("{namespace}", "my-ns").replace(
        "{service_name}",
        "my-svc",
    )
    if logs_button["onClick"]["openLink"]["url"] != expected_url:
        error_msg = f"Expected URL {expected_url}, got {logs_button['onClick']['openLink']['url']}"
        raise AssertionError(error_msg)


def test_build_issue_created_message() -> None:
    """Test building a message from an issue created event."""
    result = build_issue_created_message(IssueCreatedWebhookBodyFactory.build())
    _ = result.render()


def test_build_issue_created_message_from_example() -> None:
    """Test building a message from an example issue created JSON file."""
    with Path.open(MOCKS_DIR / "issue_created.json") as fp:
        msg = msgspec.json.decode(fp.read(), type=IssueCreatedWebhookBody)
    result = build_issue_created_message(msg)
    _ = result.render()


def test_build_issue_resolved_message_from_example() -> None:
    """Test parsing an issue resolved webhook (schema validation only)."""
    # There is no message for issue_created event, just to check schema
    with Path.open(MOCKS_DIR / "issue_resolved.json") as fp:
        msgspec.json.decode(fp.read(), type=IssueResolvedWebhookBody)


async def test_build_issue_unresolved_message_from_example() -> None:
    """Test building a message from an example issue unresolved JSON file."""
    # There is no message for issue_created event, just to check schema
    async with await open_file(MOCKS_DIR / "real" / "issue_unresolved.json") as fp:
        data = await fp.read()
        msg = msgspec.json.decode(data, type=IssueUnresolvedWebhookBody)
    build_issue_unresolved_message(msg)
