package com.mamton.aidiary.domain.model

import java.time.Instant

data class AIResult(
    val id: String,
    val requestId: String,
    val outputPayload: String,
    val status: AIResultStatus,
    val createdAt: Instant,
)
