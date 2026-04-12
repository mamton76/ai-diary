package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "entry_revisions",
    indices = [
        Index(value = ["entryId"]),
        Index(value = ["entryId", "revisionNumber"], unique = true),
    ],
)
data class EntryRevisionEntity(
    @PrimaryKey val id: String,
    val entryId: String,
    val revisionNumber: Int,
    val title: String,
    val body: String,
    val entryDateStart: String,
    val entryDateEnd: String,
    val eventStartAt: Long?,
    val eventEndAt: Long?,
    val changeType: String,
    val createdAt: Long,
)
