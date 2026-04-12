package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.UserAIContextEntity

@Dao
interface UserAIContextDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(context: UserAIContextEntity)

    @Query("SELECT * FROM user_ai_context WHERE userId = :userId")
    suspend fun getByUserId(userId: String): UserAIContextEntity?
}
