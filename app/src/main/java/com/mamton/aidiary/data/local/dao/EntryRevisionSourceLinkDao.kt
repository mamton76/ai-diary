package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.EntryRevisionSourceLinkEntity

@Dao
interface EntryRevisionSourceLinkDao {
    @Insert
    suspend fun insert(link: EntryRevisionSourceLinkEntity)

    @Query("SELECT * FROM entry_revision_source_links WHERE revisionId = :revisionId")
    suspend fun getLinksForRevision(revisionId: String): List<EntryRevisionSourceLinkEntity>
}
