package com.mamton.aidiary.domain.model

import java.time.Instant

data class AIFeedback(
    val id: String,
    val resultId: String,
    val userId: String,
    val feedbackType: AIFeedbackType,
    val comment: String? = null,
    val createdAt: Instant,
)
