package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.EntryRevisionTagEntity

@Dao
interface EntryRevisionTagDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(entity: EntryRevisionTagEntity)

    @Query("DELETE FROM entry_revision_tags WHERE revisionId = :revisionId AND tagId = :tagId")
    suspend fun delete(revisionId: String, tagId: String)

    @Query("SELECT tagId FROM entry_revision_tags WHERE revisionId = :revisionId")
    suspend fun getTagIdsForRevision(revisionId: String): List<String>
}
