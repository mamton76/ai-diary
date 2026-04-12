package com.mamton.aidiary.data.mapper

import com.mamton.aidiary.data.local.entity.EntryEntity
import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.model.EntrySource
import com.mamton.aidiary.domain.model.EntryStatus
import com.mamton.aidiary.domain.model.OriginType
import java.time.Instant
import java.time.LocalDate

fun EntryEntity.toDomain(): Entry = Entry(
    id = id,
    title = title,
    body = body,
    entryDateStart = LocalDate.parse(entryDateStart),
    entryDateEnd = LocalDate.parse(entryDateEnd),
    eventStartAt = eventStartAt?.let { Instant.ofEpochMilli(it) },
    eventEndAt = eventEndAt?.let { Instant.ofEpochMilli(it) },
    originType = runCatching { OriginType.valueOf(originType) }.getOrDefault(OriginType.USER_CREATED),
    source = runCatching { EntrySource.valueOf(source) }.getOrDefault(EntrySource.TEXT),
    status = runCatching { EntryStatus.valueOf(status) }.getOrDefault(EntryStatus.ACTIVE),
    currentRevisionId = currentRevisionId,
    createdAt = Instant.ofEpochMilli(createdAt),
    updatedAt = Instant.ofEpochMilli(updatedAt),
    isSynced = isSynced,
)

fun Entry.toEntity(): EntryEntity = EntryEntity(
    id = id,
    title = title,
    body = body,
    entryDateStart = entryDateStart.toString(),
    entryDateEnd = entryDateEnd.toString(),
    eventStartAt = eventStartAt?.toEpochMilli(),
    eventEndAt = eventEndAt?.toEpochMilli(),
    originType = originType.name,
    source = source.name,
    status = status.name,
    currentRevisionId = currentRevisionId,
    createdAt = createdAt.toEpochMilli(),
    updatedAt = updatedAt.toEpochMilli(),
    isSynced = isSynced,
)
