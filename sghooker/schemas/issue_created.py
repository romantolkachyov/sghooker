import msgspec
from msgspec import field


class ProjectData(msgspec.Struct):
    name: str
    slug: str


class IssueData(msgspec.Struct):
    web_url: str
    title: str
    culprit: str
    logger: str
    level: str
    # examples: unresolved, ...
    status: str
    # examples: new, ...
    substatus: str
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
