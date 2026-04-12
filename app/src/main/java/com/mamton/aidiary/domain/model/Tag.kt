package com.mamton.aidiary.domain.model

import java.time.Instant

data class Tag(
    val id: String,
    val userId: String,
    val type: TagType? = null,
    val source: TagSource,
    val mergedIntoTagId: String? = null,
    val createdAt: Instant,
    val updatedAt: Instant,
)
