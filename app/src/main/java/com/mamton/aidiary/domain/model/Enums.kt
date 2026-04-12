package com.mamton.aidiary.domain.model

enum class OriginType {
    USER_CREATED,
    IMPORTED,
    AI_SYNTHETIC,
}

enum class EntryStatus {
    ACTIVE,
    ARCHIVED,
    MERGED,
    DELETED,
}

enum class RevisionChangeType {
    CREATED,
    USER_EDIT,
    AI_EDIT,
    IMPORT,
    MERGE,
}

enum class TagType {
    TOPIC,
    MOOD,
    ACTIVITY,
    PERSON_LIKE,
    PLACE_LIKE,
}

enum class TagSource {
    USER,
    AI,
}

enum class AssetType {
    PHOTO,
    VIDEO,
    AUDIO,
    LINK,
    FILE,
}

enum class AssetSource {
    USER,
    AI,
}

enum class SourceLinkType {
    ENTRY_REVISION,
    AI_RESULT,
    ASSET,
    TAG,
}

enum class SourceLinkRole {
    PRIMARY_SOURCE,
    CONTEXT,
    SUPPORTING_EVIDENCE,
}

enum class AIResultStatus {
    SUCCESS,
    ERROR,
    PARTIAL,
}

enum class AIFeedbackType {
    ACCEPTED,
    REJECTED,
    EDITED,
    IGNORED,
}
