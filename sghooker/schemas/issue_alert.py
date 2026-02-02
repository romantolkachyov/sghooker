import msgspec


class FrameInfo(msgspec.Struct):
    abs_path: str
    in_app: bool
    lineno: int
    context_line: str | None = None


class StacktraceInfo(msgspec.Struct):
    frames: list[FrameInfo]


class ExceptionData(msgspec.Struct):
    type: str
    value: str
    stacktrace: StacktraceInfo


class EventException(msgspec.Struct):
    values: list[ExceptionData]


class IssueAlertEvent(msgspec.Struct):
    message: str
    culprit: str
    issue_url: str
    web_url: str
    level: str
    title: str
    tags: list[tuple[str, str]]
    release: str | None = None
    environment: str | None = None
    exception: EventException | None = None


class IssueAlertData(msgspec.Struct):
    event: IssueAlertEvent
    triggered_rule: str


class IssueAlertWebhookBody(msgspec.Struct, tag="triggered", tag_field="action"):
    """Sentry issue alert webhook body.

    https://docs.sentry.io/organization/integrations/integration-platform/webhooks/issue-alerts/
    """

    data: IssueAlertData
