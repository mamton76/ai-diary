package com.mamton.aidiary.domain.model

import java.time.Instant

data class AIContextSnapshot(
    val id: String,
    val requestId: String,
    val userAIContextVersionId: String,
    val additionalContext: String? = null,
    val createdAt: Instant,
)
