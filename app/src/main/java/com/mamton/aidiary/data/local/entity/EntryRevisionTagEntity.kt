package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index

@Entity(
    tableName = "entry_revision_tags",
    primaryKeys = ["revisionId", "tagId"],
    indices = [
        Index(value = ["tagId"]),
    ],
)
data class EntryRevisionTagEntity(
    val revisionId: String,
    val tagId: String,
    val createdAt: Long,
)
