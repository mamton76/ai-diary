package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.TagEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface TagDao {
    @Insert
    suspend fun insert(tag: TagEntity)

    @Query("SELECT * FROM tags WHERE id = :id")
    suspend fun getById(id: String): TagEntity?

    @Query("SELECT * FROM tags WHERE userId = :userId AND mergedIntoTagId IS NULL ORDER BY updatedAt DESC")
    fun observeActiveTags(userId: String): Flow<List<TagEntity>>

    @Query("DELETE FROM tags WHERE id = :id")
    suspend fun delete(id: String)
}
