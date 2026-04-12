package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index

@Entity(
    tableName = "entry_assets",
    primaryKeys = ["entryId", "assetId"],
    indices = [
        Index(value = ["assetId"]),
    ],
)
data class EntryAssetEntity(
    val entryId: String,
    val assetId: String,
)
