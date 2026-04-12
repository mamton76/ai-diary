package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.AIRequestEntity

@Dao
interface AIRequestDao {
    @Insert
    suspend fun insert(request: AIRequestEntity)

    @Query("SELECT * FROM ai_requests WHERE id = :id")
    suspend fun getById(id: String): AIRequestEntity?
}
