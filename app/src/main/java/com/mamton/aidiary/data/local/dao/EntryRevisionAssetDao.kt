package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.EntryRevisionAssetEntity

@Dao
interface EntryRevisionAssetDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(entity: EntryRevisionAssetEntity)

    @Query("SELECT assetId FROM entry_revision_assets WHERE revisionId = :revisionId")
    suspend fun getAssetIdsForRevision(revisionId: String): List<String>
}
