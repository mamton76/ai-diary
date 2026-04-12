package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "entry_revision_source_links",
    indices = [
        Index(value = ["revisionId"]),
    ],
)
data class EntryRevisionSourceLinkEntity(
    @PrimaryKey val id: String,
    val revisionId: String,
    val sourceType: String,
    val sourceId: String,
    val role: String,
    val createdAt: Long,
)
