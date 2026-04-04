package com.mamton.aidiary.data.repository

import com.mamton.aidiary.data.local.EntryDao
import com.mamton.aidiary.data.mapper.toDomain
import com.mamton.aidiary.data.mapper.toEntity
import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.model.EntrySource
import com.mamton.aidiary.domain.repository.EntryRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.time.Instant
import java.time.ZoneId
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class EntryRepositoryImpl @Inject constructor(
    private val entryDao: EntryDao,
) : EntryRepository {

    override fun getEntries(): Flow<List<Entry>> =
        entryDao.observeAll().map { entities -> entities.map { it.toDomain() } }

    override suspend fun getEntryById(id: String): Entry? =
        entryDao.getById(id)?.toDomain()

    override suspend fun createEntry(title: String, body: String): Entry {
        val now = Instant.now()
        val entry = Entry(
            id = UUID.randomUUID().toString(),
            title = title,
            body = body,
            entryDate = now.atZone(ZoneId.systemDefault()).toLocalDate(),
            source = EntrySource.TEXT,
            createdAt = now,
            updatedAt = now,
            isSynced = false,
        )
        entryDao.upsert(entry.toEntity())
        // TODO: Push to Firebase Data Connect in background
        return entry
    }

    override suspend fun syncEntries() {
        // TODO: Implement sync with Firebase Data Connect
        // 1. Fetch remote entries for current user
        // 2. Upsert into Room
        // 3. Push unsynced local entries to remote
    }
}
