from card_framework.v2 import (
    CardHeader,
    ImageType,
    Message,
    Section,
)
from card_framework.v2.card import CardWithId
from card_framework.v2.widgets import (
    Button,
    ButtonList,
    OnClick,
    OpenLink,
    TextParagraph,
)

from sghooker.schemas.issue_alert import IssueAlertWebhookBody


def build_issue_alert_message(webhook: IssueAlertWebhookBody) -> Message:
    card = CardWithId(
        header=CardHeader(
            title="CardHeaderTitle",
            image_url="https://romantolkachyov.github.io/sentry.png",
            subtitle="CardHeaderSubtitle",
            image_type=ImageType.CIRCLE,
        ),
        sections=[
            Section(
                widgets=[
                    TextParagraph(text="<b>ValueError</b>"),
                    TextParagraph(text="Exception message."),
                ]
            ),
            Section(
                collapsible=True,
                uncollapsible_widgets_count=1,
                widgets=[
                    TextParagraph(text="<b>Traceback</b>"),
                    TextParagraph(text="Formated trace."),
                    TextParagraph(text="And another"),
                ],
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
