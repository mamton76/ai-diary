package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "ai_results",
    indices = [
        Index(value = ["requestId"]),
    ],
)
data class AIResultEntity(
    @PrimaryKey val id: String,
    val requestId: String,
    val outputPayload: String,
    val status: String,
    val createdAt: Long,
)
