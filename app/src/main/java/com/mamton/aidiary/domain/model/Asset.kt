package com.mamton.aidiary.domain.model

import java.time.Instant

data class Asset(
    val id: String,
    val userId: String,
    val type: AssetType,
    val storageUrl: String? = null,
    val mimeType: String? = null,
    val originalFilename: String? = null,
    val sizeBytes: Long? = null,
    val createdAt: Instant,
    val updatedAt: Instant,
)
