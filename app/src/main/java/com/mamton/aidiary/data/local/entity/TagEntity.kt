package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "tags",
    indices = [
        Index(value = ["userId"]),
        Index(value = ["mergedIntoTagId"]),
    ],
)
data class TagEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val type: String?,
    val source: String,
    val mergedIntoTagId: String?,
    val createdAt: Long,
    val updatedAt: Long,
)
