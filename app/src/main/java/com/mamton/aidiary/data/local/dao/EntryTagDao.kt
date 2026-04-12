package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.EntryTagEntity

@Dao
interface EntryTagDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(entryTag: EntryTagEntity)

    @Query("DELETE FROM entry_tags WHERE entryId = :entryId AND tagId = :tagId")
    suspend fun delete(entryId: String, tagId: String)

    @Query("SELECT tagId FROM entry_tags WHERE entryId = :entryId")
    suspend fun getTagIdsForEntry(entryId: String): List<String>

    @Query("SELECT entryId FROM entry_tags WHERE tagId = :tagId")
    suspend fun getEntryIdsForTag(tagId: String): List<String>
}
