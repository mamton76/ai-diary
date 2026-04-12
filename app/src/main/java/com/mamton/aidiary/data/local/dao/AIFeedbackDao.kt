package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.AIFeedbackEntity

@Dao
interface AIFeedbackDao {
    @Insert
    suspend fun insert(feedback: AIFeedbackEntity)

    @Query("SELECT * FROM ai_feedback WHERE resultId = :resultId")
    suspend fun getByResultId(resultId: String): List<AIFeedbackEntity>
}
