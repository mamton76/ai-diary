package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.EntryRevisionEntity

@Dao
interface EntryRevisionDao {
    @Insert
    suspend fun insert(revision: EntryRevisionEntity)

    @Query("SELECT * FROM entry_revisions WHERE id = :id")
    suspend fun getById(id: String): EntryRevisionEntity?

    @Query("SELECT * FROM entry_revisions WHERE entryId = :entryId ORDER BY revisionNumber ASC")
    suspend fun getByEntryId(entryId: String): List<EntryRevisionEntity>

    @Query("SELECT * FROM entry_revisions WHERE entryId = :entryId ORDER BY revisionNumber DESC LIMIT 1")
    suspend fun getLatestForEntry(entryId: String): EntryRevisionEntity?

    @Query("SELECT COALESCE(MAX(revisionNumber), 0) FROM entry_revisions WHERE entryId = :entryId")
    suspend fun getMaxRevisionNumber(entryId: String): Int
}
