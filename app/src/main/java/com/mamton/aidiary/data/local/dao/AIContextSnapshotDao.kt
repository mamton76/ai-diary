package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.AIContextSnapshotEntity

@Dao
interface AIContextSnapshotDao {
    @Insert
    suspend fun insert(snapshot: AIContextSnapshotEntity)

    @Query("SELECT * FROM ai_context_snapshots WHERE requestId = :requestId")
    suspend fun getByRequestId(requestId: String): AIContextSnapshotEntity?
}
