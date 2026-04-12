package com.mamton.aidiary.data.mapper

import com.mamton.aidiary.data.local.entity.EntryRevisionEntity
import com.mamton.aidiary.domain.model.EntryRevision
import com.mamton.aidiary.domain.model.RevisionChangeType
import java.time.Instant
import java.time.LocalDate

fun EntryRevisionEntity.toDomain(): EntryRevision = EntryRevision(
    id = id,
    entryId = entryId,
    revisionNumber = revisionNumber,
    title = title,
    body = body,
    entryDateStart = LocalDate.parse(entryDateStart),
    entryDateEnd = LocalDate.parse(entryDateEnd),
    eventStartAt = eventStartAt?.let { Instant.ofEpochMilli(it) },
    eventEndAt = eventEndAt?.let { Instant.ofEpochMilli(it) },
    changeType = runCatching { RevisionChangeType.valueOf(changeType) }.getOrDefault(RevisionChangeType.CREATED),
    createdAt = Instant.ofEpochMilli(createdAt),
)

fun EntryRevision.toEntity(): EntryRevisionEntity = EntryRevisionEntity(
    id = id,
    entryId = entryId,
    revisionNumber = revisionNumber,
    title = title,
    body = body,
    entryDateStart = entryDateStart.toString(),
    entryDateEnd = entryDateEnd.toString(),
    eventStartAt = eventStartAt?.toEpochMilli(),
    eventEndAt = eventEndAt?.toEpochMilli(),
    changeType = changeType.name,
    createdAt = createdAt.toEpochMilli(),
)
