package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.AssetEntity

@Dao
interface AssetDao {
    @Insert
    suspend fun insert(asset: AssetEntity)

    @Query("SELECT * FROM assets WHERE id = :id")
    suspend fun getById(id: String): AssetEntity?

    @Query("SELECT * FROM assets WHERE userId = :userId ORDER BY createdAt DESC")
    suspend fun getByUserId(userId: String): List<AssetEntity>
}
