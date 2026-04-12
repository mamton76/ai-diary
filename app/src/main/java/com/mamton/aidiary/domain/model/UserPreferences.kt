package com.mamton.aidiary.domain.model

import java.time.Instant

data class UserPreferences(
    val id: String,
    val userId: String,
    val showAiSuggestions: Boolean = true,
    val preferences: Map<String, String> = emptyMap(),
    val createdAt: Instant,
    val updatedAt: Instant,
)
