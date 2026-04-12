package com.mamton.aidiary.data.repository

import com.mamton.aidiary.data.local.dao.AssetDao
import com.mamton.aidiary.data.local.dao.EntryAssetDao
import com.mamton.aidiary.data.local.entity.EntryAssetEntity
import com.mamton.aidiary.data.mapper.toDomain
import com.mamton.aidiary.data.mapper.toEntity
import com.mamton.aidiary.domain.model.Asset
import com.mamton.aidiary.domain.model.AssetType
import com.mamton.aidiary.domain.repository.AssetRepository
import java.time.Instant
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AssetRepositoryImpl @Inject constructor(
    private val assetDao: AssetDao,
    private val entryAssetDao: EntryAssetDao,
) : AssetRepository {

    override suspend fun createAsset(
        userId: String,
        type: AssetType,
        storageUrl: String?,
        mimeType: String?,
        originalFilename: String?,
        sizeBytes: Long?,
    ): Asset {
        val now = Instant.now()
        val asset = Asset(
            id = UUID.randomUUID().toString(),
            userId = userId,
            type = type,
            storageUrl = storageUrl,
            mimeType = mimeType,
            originalFilename = originalFilename,
            sizeBytes = sizeBytes,
            createdAt = now,
            updatedAt = now,
        )
        assetDao.insert(asset.toEntity())
        return asset
    }

    override suspend fun getAssetById(id: String): Asset? =
        assetDao.getById(id)?.toDomain()

    override suspend fun getAssetIdsForEntry(entryId: String): List<String> =
        entryAssetDao.getAssetIdsForEntry(entryId)

    override suspend fun addAssetToEntry(entryId: String, assetId: String) {
        entryAssetDao.insert(EntryAssetEntity(entryId = entryId, assetId = assetId))
    }

    override suspend fun removeAssetFromEntry(entryId: String, assetId: String) {
        entryAssetDao.delete(entryId, assetId)
    }
}
