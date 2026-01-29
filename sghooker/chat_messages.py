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
    DecoratedText,
    OnClick,
    OpenLink,
    TextParagraph,
)

from sghooker.schemas.issue_alert import (
    ExceptionData,
    IssueAlertWebhookBody,
    StacktraceInfo,
)
from sghooker.schemas.issue_created import IssueCreatedWebhookBody


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


def _exception_to_widget(exception: ExceptionData) -> list[Widget]:
    return [
        TextParagraph(
            text=f"<b>{exception.type}</b><br>{exception.value}",
        ),
        *_format_stack(exception.stacktrace),
    ]


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
                        widgets=_exception_to_widget(e),
                    )
                    for e in event.exception.values
                ]
                if event.exception
                else []
            ),
            Section(
                widgets=[
                    ButtonList(
                        buttons=[
                            Button(
                                text="View in Sentry",
                                on_click=OnClick(
                                    open_link=OpenLink(url="https://sentry.io")
                                ),
                            ),
                            Button(
                                text="Service overview",
                                type_=Button.Type.BORDERLESS,
                                on_click=OnClick(
                                    open_link=OpenLink(url="https://sentry.io")
                                ),
                            ),
                            Button(
                                text="Explore logs",
                                type_=Button.Type.BORDERLESS,
                                on_click=OnClick(
                                    open_link=OpenLink(url="https://sentry.io")
                                ),
                            ),
                        ]
                    )
                ]
            ),
        ],
    )
    return Message(cards_v2=[card])


def build_issue_created_message(webhook: IssueCreatedWebhookBody) -> Message:
    issue = webhook.data.issue
    card = CardWithId(
        header=CardHeader(
            title="New Sentry issue",
            subtitle=f"Project: {issue.project.name}",
            image_url="https://romantolkachyov.github.io/sentry.png",
            image_type=ImageType.CIRCLE,
        ),
        sections=[
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
                widgets=[
                    ButtonList(
                        buttons=[
                            Button(
                                text="View in Sentry",
                                on_click=OnClick(open_link=OpenLink(url=issue.web_url)),
                            )
                        ]
                    )
                ]
            ),
        ],
    )
    return Message(cards_v2=[card])
