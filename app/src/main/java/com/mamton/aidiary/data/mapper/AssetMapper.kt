package com.mamton.aidiary.data.mapper

import com.mamton.aidiary.data.local.entity.AssetEntity
import com.mamton.aidiary.domain.model.Asset
import com.mamton.aidiary.domain.model.AssetType
import java.time.Instant

fun AssetEntity.toDomain(): Asset = Asset(
    id = id,
    userId = userId,
    type = runCatching { AssetType.valueOf(type) }.getOrDefault(AssetType.FILE),
    storageUrl = storageUrl,
    mimeType = mimeType,
    originalFilename = originalFilename,
    sizeBytes = sizeBytes,
    createdAt = Instant.ofEpochMilli(createdAt),
    updatedAt = Instant.ofEpochMilli(updatedAt),
)

fun Asset.toEntity(): AssetEntity = AssetEntity(
    id = id,
    userId = userId,
    type = type.name,
    storageUrl = storageUrl,
    mimeType = mimeType,
    originalFilename = originalFilename,
    sizeBytes = sizeBytes,
    createdAt = createdAt.toEpochMilli(),
    updatedAt = updatedAt.toEpochMilli(),
)
