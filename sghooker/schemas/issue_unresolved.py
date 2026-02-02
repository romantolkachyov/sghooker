from typing import Any

import msgspec


class ProjectInfo(msgspec.Struct):
    id: str
    name: str
    slug: str
    platform: str | None = None


class SdkInfo(msgspec.Struct):
    name: str
    name_normalized: str


class IssueMetadata(msgspec.Struct):
    value: str
    type: str
    filename: str
    function: str
    in_app_frame_mix: str
    initial_priority: int
    sdk: SdkInfo | None = None
    title: str | None = None


class IssueInfo(msgspec.Struct):
    id: str
    shareId: str | None
    shortId: str
    title: str
    culprit: str
    permalink: str
    logger: str | None
    level: str
    status: str
    statusDetails: dict[str, Any]
    substatus: str | None
    isPublic: bool
    platform: str
    project: ProjectInfo
    type: str
    metadata: IssueMetadata
    numComments: int
    assignedTo: str | None
    isBookmarked: bool
    isSubscribed: bool
    subscriptionDetails: dict[str, Any] | None
    hasSeen: bool
    annotations: list[Any]
    issueType: str
    issueCategory: str
    priority: str
    priorityLockedAt: str | None = None


class IssueUnresolvedData(msgspec.Struct):
    issue: IssueInfo


class IssueUnresolvedWebhookBody(msgspec.Struct, tag="unresolved", tag_field="action"):
    """Sentry issue unresolved webhook body.

    Matches the structure of issue_unresolved.json
    """

    data: IssueUnresolvedData
