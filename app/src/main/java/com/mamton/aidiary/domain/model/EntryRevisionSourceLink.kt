package com.mamton.aidiary.domain.model

import java.time.Instant

data class EntryRevisionSourceLink(
    val id: String,
    val revisionId: String,
    val sourceType: SourceLinkType,
    val sourceId: String,
    val role: SourceLinkRole,
    val createdAt: Instant,
)
