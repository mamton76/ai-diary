package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.UserAIContextVersionEntity

@Dao
interface UserAIContextVersionDao {
    @Insert
    suspend fun insert(version: UserAIContextVersionEntity)

    @Query("SELECT * FROM user_ai_context_versions WHERE id = :id")
    suspend fun getById(id: String): UserAIContextVersionEntity?

    @Query("SELECT * FROM user_ai_context_versions WHERE contextId = :contextId ORDER BY versionNumber ASC")
    suspend fun getByContextId(contextId: String): List<UserAIContextVersionEntity>
}
