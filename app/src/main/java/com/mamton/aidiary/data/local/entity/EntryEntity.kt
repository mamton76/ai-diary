package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "entries",
    indices = [
        Index(value = ["entryDateStart", "entryDateEnd"]),
        Index(value = ["originType"]),
        Index(value = ["status"]),
        Index(value = ["currentRevisionId"]),
    ],
)
data class EntryEntity(
    @PrimaryKey val id: String,
    val title: String,
    val body: String,
    val entryDateStart: String,
    val entryDateEnd: String,
    val eventStartAt: Long?,
    val eventEndAt: Long?,
    val originType: String,
    val source: String,
    val status: String,
    val currentRevisionId: String?,
    val createdAt: Long,
    val updatedAt: Long,
    val isSynced: Boolean,
)
