package com.mamton.aidiary.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "assets",
    indices = [
        Index(value = ["userId"]),
    ],
)
data class AssetEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val type: String,
    val storageUrl: String?,
    val mimeType: String?,
    val originalFilename: String?,
    val sizeBytes: Long?,
    val createdAt: Long,
    val updatedAt: Long,
)
