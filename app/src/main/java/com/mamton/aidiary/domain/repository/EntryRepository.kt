package com.mamton.aidiary.domain.repository

import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.model.EntryRevision
import kotlinx.coroutines.flow.Flow

interface EntryRepository {
    fun getEntries(): Flow<List<Entry>>
    suspend fun getEntryById(id: String): Entry?
    suspend fun createEntry(title: String, body: String): Entry
    suspend fun updateEntry(id: String, title: String, body: String): Entry
    suspend fun getRevisions(entryId: String): List<EntryRevision>
    suspend fun syncEntries()
}
