import msgspec


class IssueAlertInfo(msgspec.Struct):
    title: str
    settings: list[dict[str, str]]


class IssueAlertEvent(msgspec.Struct):
    issue_url: str
    level: str
    title: str
    tags: list[tuple[str, str]]


class IssueAlertData(msgspec.Struct):
    event: IssueAlertEvent
    triggered_rule: str
    issue_alert: IssueAlertInfo


class IssueAlertWebhookBody(msgspec.Struct, tag="triggered", tag_field="action"):
    """Sentry issue alert webhook body.

    https://docs.sentry.io/organization/integrations/integration-platform/webhooks/issue-alerts/
    """

    data: IssueAlertData
