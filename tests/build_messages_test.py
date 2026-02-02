from pathlib import Path

import msgspec.json
from polyfactory.factories.msgspec_factory import MsgspecFactory

from sghooker.chat_messages import (
    build_issue_alert_message,
    build_issue_created_message,
    build_issue_unresolved_message,
)
from sghooker.schemas.alert_event import IssueAlertWebhookBody
from sghooker.schemas.issue_event import (
    IssueCreatedWebhookBody,
    IssueResolvedWebhookBody,
    IssueUnresolvedWebhookBody,
)

MOCKS_DIR = Path(__file__).parent / "mocks"


class IssueAlertWebhookBodyFactory(MsgspecFactory[IssueAlertWebhookBody]): ...


class IssueCreatedWebhookBodyFactory(MsgspecFactory[IssueCreatedWebhookBody]): ...


def test_build_issue_alert_message() -> None:
    result = build_issue_alert_message(IssueAlertWebhookBodyFactory.build())
    print("Alert: ", msgspec.json.encode(result.render()).decode())


def test_build_issue_alert_message_from_example() -> None:
    with open(MOCKS_DIR / "alert_triggered.json") as fp:
        msg = msgspec.json.decode(fp.read(), type=IssueAlertWebhookBody)
    result = build_issue_alert_message(msg)
    print("Alert: ", msgspec.json.encode(result.render()).decode())


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
