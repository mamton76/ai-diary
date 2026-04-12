package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "ai_requests",
    indices = [
        Index(value = ["userId"]),
        Index(value = ["aiContextSnapshotId"]),
    ],
)
data class AIRequestEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val requestType: String,
    val modelName: String,
    val promptVersion: String?,
    val inputPayload: String,
    val aiContextSnapshotId: String?,
    val createdAt: Long,
)
