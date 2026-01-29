import msgspec.json
from polyfactory.factories.msgspec_factory import MsgspecFactory

from sghooker.chat_messages import build_issue_alert_message
from sghooker.schemas.issue_alert import IssueAlertWebhookBody


class IssueAlertWebhookBodyFactory(MsgspecFactory[IssueAlertWebhookBody]): ...


def test_build_issue_alert_message() -> None:
    result = build_issue_alert_message(IssueAlertWebhookBodyFactory.build())
    print(msgspec.json.encode(result.render()).decode())


# async def test_send_message():
#     result = build_issue_alert_message(IssueAlertWebhookBodyFactory.build())
#     await send_message(result.render())
