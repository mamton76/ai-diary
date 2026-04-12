package com.mamton.aidiary.domain.model

import java.time.Instant

data class TagLabel(
    val id: String,
    val tagId: String,
    val text: String,
    val normalizedText: String,
    val isPrimary: Boolean,
    val locale: String? = null,
    val source: TagSource,
    val createdAt: Instant,
    val updatedAt: Instant,
)
