package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index

@Entity(
    tableName = "entry_revision_assets",
    primaryKeys = ["revisionId", "assetId"],
    indices = [
        Index(value = ["assetId"]),
    ],
)
data class EntryRevisionAssetEntity(
    val revisionId: String,
    val assetId: String,
    val createdAt: Long,
)
