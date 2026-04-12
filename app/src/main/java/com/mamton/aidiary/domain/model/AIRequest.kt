package com.mamton.aidiary.domain.model

import java.time.Instant

data class AIRequest(
    val id: String,
    val userId: String,
    val requestType: String,
    val modelName: String,
    val promptVersion: String? = null,
    val inputPayload: String,
    val aiContextSnapshotId: String? = null,
    val createdAt: Instant,
)
