package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "ai_context_snapshots",
    indices = [
        Index(value = ["requestId"]),
        Index(value = ["userAIContextVersionId"]),
    ],
)
data class AIContextSnapshotEntity(
    @PrimaryKey val id: String,
    val requestId: String,
    val userAIContextVersionId: String,
    val additionalContext: String?,
    val createdAt: Long,
)
