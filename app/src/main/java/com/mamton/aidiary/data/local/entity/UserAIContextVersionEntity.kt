package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "user_ai_context_versions",
    indices = [
        Index(value = ["contextId"]),
    ],
)
data class UserAIContextVersionEntity(
    @PrimaryKey val id: String,
    val contextId: String,
    val versionNumber: Int,
    val renderedContext: String?,
    val structuredSignals: String?,
    val changeReason: String?,
    val createdAt: Long,
)
