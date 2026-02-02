import msgspec
from msgspec import field


class ProjectData(msgspec.Struct):
    name: str
    slug: str


class IssueData(msgspec.Struct):
    permalink: str
    title: str
    culprit: str
    logger: str
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
    issue: IssueData


class BaseIssueWebhookBody(msgspec.Struct):
    data: IssueWebhookData


class IssueCreatedWebhookBody(BaseIssueWebhookBody, tag="created", tag_field="action"):
    pass


class IssueResolvedWebhookBody(
    BaseIssueWebhookBody, tag="resolved", tag_field="action"
):
    """Sentry issue resolved webhook body."""

    pass


class IssueUnresolvedWebhookBody(
    BaseIssueWebhookBody, tag="unresolved", tag_field="action"
):
    """Sentry issue unresolved webhook body."""

    pass
