package com.mamton.aidiary.domain.repository

import com.mamton.aidiary.domain.model.Asset
import com.mamton.aidiary.domain.model.AssetType

interface AssetRepository {
    suspend fun createAsset(
        userId: String,
        type: AssetType,
        storageUrl: String? = null,
        mimeType: String? = null,
        originalFilename: String? = null,
        sizeBytes: Long? = null,
    ): Asset
    suspend fun getAssetById(id: String): Asset?
    suspend fun getAssetIdsForEntry(entryId: String): List<String>
    suspend fun addAssetToEntry(entryId: String, assetId: String)
    suspend fun removeAssetFromEntry(entryId: String, assetId: String)
}
