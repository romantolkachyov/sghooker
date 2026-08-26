"""Issue event schema models for Sentry webhook payloads."""

import msgspec
from msgspec import field


class ProjectData(msgspec.Struct):
    """Data about a Sentry project."""

    name: str
    slug: str


class IssueData(msgspec.Struct):
    """Data about a Sentry issue."""

    permalink: str
    title: str
    culprit: str
    logger: str | None
    level: str
    # examples: unresolved, ...
    status: str
    # examples: new, ...
    substatus: str | None
    project: ProjectData
    # examples: default, ...
    type: str
    # examples: high, ...
    priority: str
    # examples: error, ...
    issue_type: str = field(name="issueType")
    # examples: error, ...
    issue_category: str = field(name="issueCategory")
    count: str
    user_count: int = field(name="userCount")


class IssueWebhookData(msgspec.Struct):
    """Data payload for an issue webhook."""

    issue: IssueData


class BaseIssueWebhookBody(msgspec.Struct):
    """Base class for issue webhook bodies."""

    data: IssueWebhookData


class IssueCreatedWebhookBody(BaseIssueWebhookBody):
    """Sentry issue created webhook body.

    Untagged: ``action`` is also ``created`` for ``error.created`` webhooks.
    """


class IssueResolvedWebhookBody(
    BaseIssueWebhookBody,
    tag="resolved",
    tag_field="action",
):
    """Sentry issue resolved webhook body."""


class IssueUnresolvedWebhookBody(
    BaseIssueWebhookBody,
    tag="unresolved",
    tag_field="action",
):
    """Sentry issue unresolved webhook body."""
