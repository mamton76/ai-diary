package com.mamton.aidiary.data.remote

import com.google.firebase.Timestamp
import com.mamton.aidiary.dataconnect.generated.DiaryConnector
import com.mamton.aidiary.dataconnect.generated.ListEntriesByUserQuery
import com.mamton.aidiary.dataconnect.generated.execute
import com.mamton.aidiary.dataconnect.generated.instance
import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.model.EntrySource
import com.mamton.aidiary.domain.model.EntryStatus
import com.mamton.aidiary.domain.model.OriginType
import java.time.Instant
import java.time.LocalDate
import com.google.firebase.dataconnect.LocalDate as FdcLocalDate

class EntryRemoteDataSource {

    private val connector get() = DiaryConnector.instance

    suspend fun fetchEntries(uid: String): List<Entry> {
        val result = connector.listEntriesByUser.execute(uid = uid)
        return result.data.entries.map { it.toDomain() }
    }

    suspend fun upsertEntry(uid: String, entry: Entry) {
        connector.upsertEntry.execute(
            id = entry.id,
            uid = uid,
            title = entry.title,
            body = entry.body,
            entryDateStart = entry.entryDateStart.toFdcLocalDate(),
            entryDateEnd = entry.entryDateEnd.toFdcLocalDate(),
            originType = entry.originType.name,
            source = entry.source.name,
            status = entry.status.name,
            createdAt = entry.createdAt.toTimestamp(),
            updatedAt = entry.updatedAt.toTimestamp(),
        ) {
            eventStartAt = entry.eventStartAt?.toTimestamp()
            eventEndAt = entry.eventEndAt?.toTimestamp()
            currentRevisionId = entry.currentRevisionId
        }
    }
}

private fun ListEntriesByUserQuery.Data.EntriesItem.toDomain(): Entry = Entry(
    id = id,
    title = title,
    body = body,
    entryDateStart = LocalDate.of(entryDateStart.year, entryDateStart.month, entryDateStart.day),
    entryDateEnd = LocalDate.of(entryDateEnd.year, entryDateEnd.month, entryDateEnd.day),
    eventStartAt = eventStartAt?.let { Instant.ofEpochSecond(it.seconds, it.nanoseconds.toLong()) },
    eventEndAt = eventEndAt?.let { Instant.ofEpochSecond(it.seconds, it.nanoseconds.toLong()) },
    originType = runCatching { OriginType.valueOf(originType) }.getOrDefault(OriginType.USER_CREATED),
    source = runCatching { EntrySource.valueOf(source) }.getOrDefault(EntrySource.TEXT),
    status = runCatching { EntryStatus.valueOf(status) }.getOrDefault(EntryStatus.ACTIVE),
    currentRevisionId = currentRevisionId,
    createdAt = Instant.ofEpochSecond(createdAt.seconds, createdAt.nanoseconds.toLong()),
    updatedAt = Instant.ofEpochSecond(updatedAt.seconds, updatedAt.nanoseconds.toLong()),
    isSynced = true,
)

private fun LocalDate.toFdcLocalDate(): FdcLocalDate =
    FdcLocalDate(year = year, month = monthValue, day = dayOfMonth)

private fun Instant.toTimestamp(): Timestamp =
    Timestamp(epochSecond, nano)
