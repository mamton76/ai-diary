package com.mamton.aidiary.data.repository

import com.google.firebase.auth.FirebaseAuth
import com.mamton.aidiary.data.local.dao.EntryDao
import com.mamton.aidiary.data.local.dao.EntryRevisionDao
import com.mamton.aidiary.data.local.entity.EntryRevisionEntity
import com.mamton.aidiary.data.mapper.toDomain
import com.mamton.aidiary.data.mapper.toEntity
import com.mamton.aidiary.data.remote.EntryRemoteDataSource
import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.model.EntryRevision
import com.mamton.aidiary.domain.model.EntrySource
import com.mamton.aidiary.domain.model.EntryStatus
import com.mamton.aidiary.domain.model.OriginType
import com.mamton.aidiary.domain.model.RevisionChangeType
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
    private val entryRevisionDao: EntryRevisionDao,
    private val remoteDataSource: EntryRemoteDataSource,
    private val firebaseAuth: FirebaseAuth,
) : EntryRepository {

    override fun getEntries(): Flow<List<Entry>> =
        entryDao.observeAll().map { entities -> entities.map { it.toDomain() } }

    override suspend fun getEntryById(id: String): Entry? =
        entryDao.getById(id)?.toDomain()

    override suspend fun createEntry(title: String, body: String): Entry {
        val now = Instant.now()
        val today = now.atZone(ZoneId.systemDefault()).toLocalDate()
        val entryId = UUID.randomUUID().toString()
        val revisionId = UUID.randomUUID().toString()

        val entry = Entry(
            id = entryId,
            title = title,
            body = body,
            entryDateStart = today,
            entryDateEnd = today,
            originType = OriginType.USER_CREATED,
            source = EntrySource.TEXT,
            status = EntryStatus.ACTIVE,
            currentRevisionId = revisionId,
            createdAt = now,
            updatedAt = now,
            isSynced = false,
        )
        entryDao.upsert(entry.toEntity())

        val revision = EntryRevisionEntity(
            id = revisionId,
            entryId = entryId,
            revisionNumber = 1,
            title = title,
            body = body,
            entryDateStart = today.toString(),
            entryDateEnd = today.toString(),
            eventStartAt = null,
            eventEndAt = null,
            changeType = RevisionChangeType.CREATED.name,
            createdAt = now.toEpochMilli(),
        )
        entryRevisionDao.insert(revision)

        pushToRemote(entry)
        return entry
    }

    override suspend fun updateEntry(id: String, title: String, body: String): Entry {
        val existing = entryDao.getById(id)?.toDomain()
            ?: throw IllegalArgumentException("Entry not found: $id")

        val now = Instant.now()
        val nextRevisionNumber = entryRevisionDao.getMaxRevisionNumber(id) + 1
        val revisionId = UUID.randomUUID().toString()

        val revision = EntryRevisionEntity(
            id = revisionId,
            entryId = id,
            revisionNumber = nextRevisionNumber,
            title = title,
            body = body,
            entryDateStart = existing.entryDateStart.toString(),
            entryDateEnd = existing.entryDateEnd.toString(),
            eventStartAt = existing.eventStartAt?.toEpochMilli(),
            eventEndAt = existing.eventEndAt?.toEpochMilli(),
            changeType = RevisionChangeType.USER_EDIT.name,
            createdAt = now.toEpochMilli(),
        )
        entryRevisionDao.insert(revision)

        val updated = existing.copy(
            title = title,
            body = body,
            currentRevisionId = revisionId,
            updatedAt = now,
            isSynced = false,
        )
        entryDao.upsert(updated.toEntity())

        pushToRemote(updated)
        return updated
    }

    override suspend fun getRevisions(entryId: String): List<EntryRevision> =
        entryRevisionDao.getByEntryId(entryId).map { it.toDomain() }

    override suspend fun syncEntries() {
        val uid = firebaseAuth.currentUser?.uid ?: return

        try {
            val remoteEntries = remoteDataSource.fetchEntries(uid)
            val entities = remoteEntries.map { it.copy(isSynced = true).toEntity() }
            entryDao.upsertAll(entities)
        } catch (_: Exception) {
        }

        val unsynced = entryDao.getUnsynced()
        for (entity in unsynced) {
            try {
                remoteDataSource.upsertEntry(uid, entity.toDomain())
                entryDao.markSynced(entity.id)
            } catch (_: Exception) {
            }
        }
    }

    private suspend fun pushToRemote(entry: Entry) {
        val uid = firebaseAuth.currentUser?.uid ?: return
        try {
            remoteDataSource.upsertEntry(uid, entry)
            entryDao.markSynced(entry.id)
        } catch (_: Exception) {
        }
    }
}
