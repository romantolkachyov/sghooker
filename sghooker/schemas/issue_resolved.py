from typing import Any

import msgspec


class ProjectInfo(msgspec.Struct):
    id: str
    name: str
    slug: str
    platform: str


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
    priorityLockedAt: str | None
    # Fields specific to or present in resolved/snapshot data
    seerFixabilityScore: float | None
    seerAutofixLastTriggered: str | None
    isUnhandled: bool
    count: str
    userCount: int
    firstSeen: str
    lastSeen: str


class ActorInfo(msgspec.Struct):
    type: str
    id: int
    name: str


class InstallationInfo(msgspec.Struct):
    uuid: str


class IssueResolvedData(msgspec.Struct):
    resolution_type: str
    issue: IssueInfo


class IssueResolvedWebhookBody(msgspec.Struct, tag="resolved", tag_field="action"):
    """Sentry issue resolved webhook body.

    Matches the structure of issue_resolved.json
    """

    installation: InstallationInfo
    data: IssueResolvedData
    actor: ActorInfo
