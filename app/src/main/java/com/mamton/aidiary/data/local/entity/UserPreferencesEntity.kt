package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "user_preferences",
    indices = [
        Index(value = ["userId"], unique = true),
    ],
)
data class UserPreferencesEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val showAiSuggestions: Boolean,
    val preferences: String,
    val createdAt: Long,
    val updatedAt: Long,
)
