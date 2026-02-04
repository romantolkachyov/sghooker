"""Chat message builders for Sentry webhook events."""

from card_framework.v2 import (
    CardHeader,
    ImageType,
    Message,
    Section,
    Widget,
)
from card_framework.v2.card import CardWithId
from card_framework.v2.widgets import (
    Button,
    ButtonList,
    Chip,
    ChipList,
    DecoratedText,
    OnClick,
    OpenLink,
    TextParagraph,
)

from sghooker.schemas.alert_event import (
    AlertEventWebhookBody,
    ExceptionData,
    StacktraceInfo,
)
from sghooker.schemas.issue_event import (
    IssueCreatedWebhookBody,
    IssueData,
    IssueUnresolvedWebhookBody,
)


def _get_tag_value(tags: list[tuple[str, str]], key: str) -> str | None:
    """Get the value of a tag by its key.

    Args:
        tags: A list of tuples containing tag key-value pairs.
        key: The key to search for.

    Returns:
        The value associated with the key, or None if not found.

    """
    for k, v in tags:
        if k == key:
            return v
    return None


def _format_stack(stack_info: StacktraceInfo) -> list[DecoratedText]:
    """Format a stack trace into a list of decorated text widgets.

    Args:
        stack_info: The stack trace information containing frames.

    Returns:
        A list of decorated text widgets representing the stack trace.

    """
    data = []
    for frame in stack_info.frames:
        if not frame.in_app:
            continue
        context_line = f"&nbsp;&nbsp;{frame.context_line}"
        data.append(
            DecoratedText(
                text=f"{context_line}",
                top_label=f"{frame.abs_path}:{frame.lineno}",
                wrap_text=False,
            ),
        )
    return data


def _exception_to_widgets(exception: ExceptionData) -> list[Widget]:
    """Convert an exception to a list of widgets.

    Args:
        exception: The exception data containing type, value, and stacktrace.

    Returns:
        A list of widgets representing the exception.

    """
    return [
        TextParagraph(
            text=f"<b>{exception.type}</b><br>{exception.value}",
        ),
        *_format_stack(exception.stacktrace),
    ]


def _issue_buttons(
    issue_url: str,
    namespace: str | None = None,
    service_name: str | None = None,
    trace_id: str | None = None,
    logs_url: str | None = None,
) -> list[Button]:
    """Create a list of buttons for an issue.

    Args:
        issue_url: The URL to the issue in Sentry.
        namespace: The namespace of the service (optional).
        service_name: The name of the service (optional).
        trace_id: The trace ID (optional).
        logs_url: The URL to the logs (optional).

    Returns:
        A list of buttons for the issue.

    """
    buttons = [
        Button(
            text="Open sentry.io",
            on_click=OnClick(open_link=OpenLink(url=issue_url)),
        ),
    ]
    if namespace and service_name:
        buttons.append(
            Button(
                text="Dashboard",
                type_=Button.Type.BORDERLESS,
                on_click=OnClick(open_link=OpenLink(url="about:blank")),
            ),
        )
        if logs_url:
            buttons.append(
                Button(
                    text="Logs",
                    type_=Button.Type.BORDERLESS,
                    on_click=OnClick(open_link=OpenLink(url=logs_url)),
                ),
            )
    if trace_id:
        buttons.append(
            Button(
                text="Jump to trace",
                type_=Button.Type.BORDERLESS,
                on_click=OnClick(open_link=OpenLink(url="about:blank")),
            ),
        )
    return buttons


def build_alert_event_message(
    webhook: AlertEventWebhookBody,
    grafana_url_template: str | None = None,
) -> Message:
    """Build a Google Chat message from an alert event webhook.

    Args:
        webhook: The alert event webhook body.
        grafana_url_template: Optional Grafana URL template for log links.

    Returns:
        A Google Chat message with the alert details.

    """
    event = webhook.data.event
    namespace = _get_tag_value(event.tags, "namespace")
    service_name = _get_tag_value(event.tags, "service_name")
    logs_url = None
    if grafana_url_template and namespace and service_name:
        logs_url = grafana_url_template.replace("{namespace}", namespace).replace(
            "{service_name}",
            service_name,
        )

    card = CardWithId(
        header=CardHeader(
            title=event.title,
            subtitle=f"{event.release}&nbsp;—&nbsp;<b>{event.environment}</b>",
            image_url="https://romantolkachyov.github.io/sentry.png",
            image_type=ImageType.CIRCLE,
        ),
        sections=[
            Section(
                widgets=[
                    TextParagraph(text=f"<b>culprit:</b> {webhook.data.event.culprit}"),
                    TextParagraph(text=event.message, max_lines=4),
                ],
            ),
            *(
                [
                    Section(
                        collapsible=True,
                        uncollapsible_widgets_count=1,
                        widgets=_exception_to_widgets(e),
                    )
                    for e in event.exception.values
                ]
                if event.exception
                else []
            ),
            Section(
                widgets=[
                    ChipList(
                        layout=ChipList.Layout.HORIZONTAL_SCROLLABLE,
                        chips=[Chip(label=f"{tag[0]} | {tag[1]}", disabled=True) for tag in event.tags],
                    ),
                ],
            ),
            Section(
                widgets=[
                    ButtonList(
                        buttons=_issue_buttons(
                            issue_url=event.web_url,
                            namespace=namespace,
                            service_name=service_name,
                            logs_url=logs_url,
                        ),
                    ),
                ],
            ),
        ],
    )
    return Message(cards_v2=[card])


def _issue_sections(issue: IssueData) -> list[Section]:
    """Build sections for an issue.

    Args:
        issue: The issue data containing details about the issue.

    Returns:
        A list of sections representing the issue.

    """
    return [
        Section(widgets=[TextParagraph(text=f"<b>culprit:</b> {issue.culprit}")]),
        Section(widgets=[TextParagraph(text=issue.title, max_lines=4)]),
        Section(
            widgets=[
                TextParagraph(
                    text="&nbsp;&nbsp;".join(
                        [
                            f"Priority: <b>{issue.priority}</b>",
                            f"Count: <b>{issue.count}</b>",
                            f"Users: <b>{issue.user_count}</b>",
                        ],
                    ),
                ),
            ],
        ),
        Section(
            widgets=[ButtonList(buttons=_issue_buttons(issue_url=issue.permalink))],
        ),
    ]


def build_issue_created_message(webhook: IssueCreatedWebhookBody) -> Message:
    """Build a Google Chat message from an issue created webhook.

    Args:
        webhook: The issue created webhook body.

    Returns:
        A Google Chat message with the issue details.

    """
    issue = webhook.data.issue
    card = CardWithId(
        header=CardHeader(
            title="New Sentry issue",
            subtitle=f"Project: {issue.project.name}",
            image_url="https://romantolkachyov.github.io/sentry.png",
            image_type=ImageType.CIRCLE,
        ),
        sections=_issue_sections(issue),
    )
    return Message(cards_v2=[card])


def build_issue_unresolved_message(webhook: IssueUnresolvedWebhookBody) -> Message:
    """Build a Google Chat message from an issue unresolved webhook.

    Args:
        webhook: The issue unresolved webhook body.

    Returns:
        A Google Chat message with the issue details.

    """
    issue = webhook.data.issue
    return Message(
        cards_v2=[
            CardWithId(
                header=CardHeader(
                    title=f"Issue unresolved ({issue.substatus})",
                    subtitle=f"Project: {issue.project.name}",
                    image_url="https://romantolkachyov.github.io/sentry.png",
                    image_type=ImageType.CIRCLE,
                ),
                sections=_issue_sections(issue),
            ),
        ],
    )
