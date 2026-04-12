package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "ai_feedback",
    indices = [
        Index(value = ["resultId"]),
    ],
)
data class AIFeedbackEntity(
    @PrimaryKey val id: String,
    val resultId: String,
    val userId: String,
    val feedbackType: String,
    val comment: String?,
    val createdAt: Long,
)
