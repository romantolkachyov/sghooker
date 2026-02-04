from pathlib import Path

import msgspec.json
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


class AlertEventWebhookBodyFactory(MsgspecFactory[AlertEventWebhookBody]): ...


class IssueCreatedWebhookBodyFactory(MsgspecFactory[IssueCreatedWebhookBody]): ...


def test_build_alert_event_message() -> None:
    result = build_alert_event_message(AlertEventWebhookBodyFactory.build())
    print("Alert: ", msgspec.json.encode(result.render()).decode())


def test_build_alert_event_message_from_example() -> None:
    with open(MOCKS_DIR / "alert_triggered.json") as fp:
        msg = msgspec.json.decode(fp.read(), type=AlertEventWebhookBody)
    result = build_alert_event_message(msg)
    print("Alert: ", msgspec.json.encode(result.render()).decode())


def test_build_alert_event_message_with_grafana_url() -> None:
    with open(MOCKS_DIR / "alert_triggered.json") as fp:
        msg = msgspec.json.decode(fp.read(), type=AlertEventWebhookBody)
    # Add required tags to the mock data if they are missing
    msg.data.event.tags.append(("namespace", "my-ns"))
    msg.data.event.tags.append(("service_name", "my-svc"))

    template = 'https://grafana.example.com/explore?left=["now-1h","now","Loki",{"expr":"{{namespace=\'{namespace}\',service_name=\'{service_name}\'}}"}]'
    result = build_alert_event_message(msg, grafana_url_template=template)
    rendered = result.render()

    # Find the Logs button in the rendered card
    buttons = rendered["cardsV2"][0]["card"]["sections"][-1]["widgets"][0][
        "buttonList"
    ]["buttons"]
    logs_button = next(b for b in buttons if b["text"] == "Logs")
    expected_url = template.replace("{namespace}", "my-ns").replace(
        "{service_name}", "my-svc"
    )
    assert logs_button["onClick"]["openLink"]["url"] == expected_url


def test_build_issue_created_message() -> None:
    result = build_issue_created_message(IssueCreatedWebhookBodyFactory.build())
    print("Created: ", msgspec.json.encode(result.render()).decode())


def test_build_issue_created_message_from_example() -> None:
    with open(MOCKS_DIR / "issue_created.json") as fp:
        msg = msgspec.json.decode(fp.read(), type=IssueCreatedWebhookBody)
    result = build_issue_created_message(msg)
    print("Created: ", msgspec.json.encode(result.render()).decode())


def test_build_issue_resolved_message_from_example() -> None:
    # There is no message for issue_created event, just to check schema
    with open(MOCKS_DIR / "issue_resolved.json") as fp:
        msgspec.json.decode(fp.read(), type=IssueResolvedWebhookBody)


async def test_build_issue_unresolved_message_from_example() -> None:
    # There is no message for issue_created event, just to check schema
    with open(MOCKS_DIR / "real" / "issue_unresolved.json") as fp:
        msg = msgspec.json.decode(fp.read(), type=IssueUnresolvedWebhookBody)
    build_issue_unresolved_message(msg)


# async def test_send_message():
#     result = build_issue_alert_message(IssueAlertWebhookBodyFactory.build())
#     await send_message(result.render())
