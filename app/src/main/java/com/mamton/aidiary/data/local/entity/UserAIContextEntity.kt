package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "user_ai_context",
    indices = [
        Index(value = ["userId"], unique = true),
    ],
)
data class UserAIContextEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val currentVersionId: String?,
    val renderedContext: String?,
    val structuredSignals: String?,
    val createdAt: Long,
    val updatedAt: Long,
)
