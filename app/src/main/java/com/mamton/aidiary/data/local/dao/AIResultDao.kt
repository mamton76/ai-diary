package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.AIResultEntity

@Dao
interface AIResultDao {
    @Insert
    suspend fun insert(result: AIResultEntity)

    @Query("SELECT * FROM ai_results WHERE requestId = :requestId")
    suspend fun getByRequestId(requestId: String): List<AIResultEntity>
}
