package com.mamton.aidiary.domain.model

import java.time.Instant

data class UserAIContext(
    val id: String,
    val userId: String,
    val currentVersionId: String? = null,
    val renderedContext: String? = null,
    val structuredSignals: String? = null,
    val createdAt: Instant,
    val updatedAt: Instant,
)
