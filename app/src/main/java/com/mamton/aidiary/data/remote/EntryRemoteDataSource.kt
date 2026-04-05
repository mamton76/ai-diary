package com.mamton.aidiary.data.remote

import com.google.firebase.Timestamp
import com.mamton.aidiary.dataconnect.generated.DiaryConnector
import com.mamton.aidiary.dataconnect.generated.ListEntriesByUserQuery
import com.mamton.aidiary.dataconnect.generated.execute
import com.mamton.aidiary.dataconnect.generated.instance
import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.model.EntrySource
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
            entryDate = entry.entryDate.toFdcLocalDate(),
            source = entry.source.name,
            createdAt = entry.createdAt.toTimestamp(),
            updatedAt = entry.updatedAt.toTimestamp(),
        )
    }
}

private fun ListEntriesByUserQuery.Data.EntriesItem.toDomain(): Entry = Entry(
    id = id,
    title = title,
    body = body,
    entryDate = LocalDate.of(entryDate.year, entryDate.month, entryDate.day),
    source = runCatching { EntrySource.valueOf(source) }.getOrDefault(EntrySource.TEXT),
    createdAt = Instant.ofEpochSecond(createdAt.seconds, createdAt.nanoseconds.toLong()),
    updatedAt = Instant.ofEpochSecond(updatedAt.seconds, updatedAt.nanoseconds.toLong()),
    isSynced = true,
)

private fun LocalDate.toFdcLocalDate(): FdcLocalDate =
    FdcLocalDate(year = year, month = monthValue, day = dayOfMonth)

private fun Instant.toTimestamp(): Timestamp =
    Timestamp(epochSecond, nano)
