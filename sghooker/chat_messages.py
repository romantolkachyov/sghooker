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
    ExceptionData,
    IssueAlertWebhookBody,
    StacktraceInfo,
)
from sghooker.schemas.issue_event import (
    IssueCreatedWebhookBody,
    IssueData,
    IssueUnresolvedWebhookBody,
)


def _format_stack(stack_info: StacktraceInfo) -> list[DecoratedText]:
    # data = ["<pre><code>"]
    data = []
    for frame in stack_info.frames:
        if not frame.in_app:
            continue
        context_line = f"&nbsp;&nbsp;{frame.context_line}"  # .replace(" ", "&nbsp;")
        # data.append(DecoratedText(text=f"&nbsp;{frame.abs_path}", wrap_text=False))
        data.append(
            DecoratedText(
                text=f"{context_line}",
                top_label=f"{frame.abs_path}:{frame.lineno}",
                wrap_text=False,
            )
        )
    # data.append("</code></pre>")
    return data


def _exception_to_widgets(exception: ExceptionData) -> list[Widget]:
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
) -> list[Button]:
    buttons = [
        Button(
            text="Open sentry.io",
            on_click=OnClick(open_link=OpenLink(url=issue_url)),
        )
    ]
    if namespace and service_name:
        buttons.extend(
            [
                Button(
                    text="Dashboard",
                    type_=Button.Type.BORDERLESS,
                    on_click=OnClick(open_link=OpenLink(url="about:blank")),
                ),
                Button(
                    text="Logs",
                    type_=Button.Type.BORDERLESS,
                    on_click=OnClick(open_link=OpenLink(url="about:blank")),
                ),
            ]
        )
    if trace_id:
        buttons.append(
            Button(
                text="Jump to trace",
                type_=Button.Type.BORDERLESS,
                on_click=OnClick(open_link=OpenLink(url="about:blank")),
            )
        )
    return buttons


def build_issue_alert_message(webhook: IssueAlertWebhookBody) -> Message:
    event = webhook.data.event
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
                ]
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
                        chips=[
                            Chip(label=f"{tag[0]} | {tag[1]}", disabled=True)
                            for tag in event.tags
                        ],
                    )
                ]
            ),
            Section(
                widgets=[ButtonList(buttons=_issue_buttons(issue_url=event.web_url))]
            ),
        ],
    )
    return Message(cards_v2=[card])


def _issue_sections(issue: IssueData) -> list[Section]:
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
                        ]
                    )
                )
            ]
        ),
        Section(
            widgets=[ButtonList(buttons=_issue_buttons(issue_url=issue.permalink))]
        ),
    ]


def build_issue_created_message(webhook: IssueCreatedWebhookBody) -> Message:
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
            )
        ]
    )
