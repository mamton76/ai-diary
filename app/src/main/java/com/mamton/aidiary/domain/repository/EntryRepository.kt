package com.mamton.aidiary.domain.repository

import com.mamton.aidiary.domain.model.Entry
import kotlinx.coroutines.flow.Flow

interface EntryRepository {
    fun getEntries(): Flow<List<Entry>>
    suspend fun getEntryById(id: String): Entry?
    suspend fun createEntry(title: String, body: String): Entry
    suspend fun syncEntries()
}
