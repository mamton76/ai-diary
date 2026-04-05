package com.mamton.aidiary.data.repository

import com.google.firebase.auth.FirebaseAuth
import com.mamton.aidiary.data.local.EntryDao
import com.mamton.aidiary.data.mapper.toDomain
import com.mamton.aidiary.data.mapper.toEntity
import com.mamton.aidiary.data.remote.EntryRemoteDataSource
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
    private val remoteDataSource: EntryRemoteDataSource,
    private val firebaseAuth: FirebaseAuth,
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

        // Push to remote in background (best-effort for MVP)
        val uid = firebaseAuth.currentUser?.uid
        if (uid != null) {
            try {
                remoteDataSource.upsertEntry(uid, entry)
                entryDao.markSynced(entry.id)
            } catch (_: Exception) {
                // Entry stays isSynced=false, will be pushed on next sync
            }
        }

        return entry
    }

    override suspend fun syncEntries() {
        val uid = firebaseAuth.currentUser?.uid ?: return

        // 1. Pull remote entries and upsert into Room
        try {
            val remoteEntries = remoteDataSource.fetchEntries(uid)
            val entities = remoteEntries.map { it.copy(isSynced = true).toEntity() }
            entryDao.upsertAll(entities)
        } catch (_: Exception) {
            // Offline or error — skip pull, continue with push
        }

        // 2. Push unsynced local entries to remote
        val unsynced = entryDao.getUnsynced()
        for (entity in unsynced) {
            try {
                remoteDataSource.upsertEntry(uid, entity.toDomain())
                entryDao.markSynced(entity.id)
            } catch (_: Exception) {
                // Will retry on next sync
            }
        }
    }
}
