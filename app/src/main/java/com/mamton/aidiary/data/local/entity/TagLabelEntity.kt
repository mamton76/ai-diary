package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "tag_labels",
    indices = [
        Index(value = ["tagId"]),
        Index(value = ["normalizedText"]),
    ],
)
data class TagLabelEntity(
    @PrimaryKey val id: String,
    val tagId: String,
    val text: String,
    val normalizedText: String,
    val isPrimary: Boolean,
    val locale: String?,
    val source: String,
    val createdAt: Long,
    val updatedAt: Long,
)
