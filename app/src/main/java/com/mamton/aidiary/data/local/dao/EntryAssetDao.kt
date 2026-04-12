package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.EntryAssetEntity

@Dao
interface EntryAssetDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(entity: EntryAssetEntity)

    @Query("DELETE FROM entry_assets WHERE entryId = :entryId AND assetId = :assetId")
    suspend fun delete(entryId: String, assetId: String)

    @Query("SELECT assetId FROM entry_assets WHERE entryId = :entryId")
    suspend fun getAssetIdsForEntry(entryId: String): List<String>
}
