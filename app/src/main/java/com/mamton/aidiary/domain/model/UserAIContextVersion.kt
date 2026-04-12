package com.mamton.aidiary.domain.model

import java.time.Instant

data class UserAIContextVersion(
    val id: String,
    val contextId: String,
    val versionNumber: Int,
    val renderedContext: String? = null,
    val structuredSignals: String? = null,
    val changeReason: String? = null,
    val createdAt: Instant,
)
