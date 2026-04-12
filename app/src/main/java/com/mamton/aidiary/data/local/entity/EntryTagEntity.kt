package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index

@Entity(
    tableName = "entry_tags",
    primaryKeys = ["entryId", "tagId"],
    indices = [
        Index(value = ["tagId"]),
    ],
)
data class EntryTagEntity(
    val entryId: String,
    val tagId: String,
)
