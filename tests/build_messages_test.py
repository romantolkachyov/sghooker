from pathlib import Path

import msgspec.json
from polyfactory.factories.msgspec_factory import MsgspecFactory

from sghooker.chat_messages import (
    build_issue_alert_message,
    build_issue_created_message,
)
from sghooker.schemas.issue_alert import IssueAlertWebhookBody
from sghooker.schemas.issue_created import IssueCreatedWebhookBody
from sghooker.schemas.issue_resolved import IssueResolvedWebhookBody
from sghooker.schemas.issue_unresolved import IssueUnresolvedWebhookBody

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


# async def test_send_message():
#     result = build_issue_alert_message(IssueAlertWebhookBodyFactory.build())
#     await send_message(result.render())
