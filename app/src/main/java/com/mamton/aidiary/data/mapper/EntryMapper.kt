package com.mamton.aidiary.data.mapper

import com.mamton.aidiary.data.local.EntryEntity
import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.model.EntrySource
import java.time.Instant
import java.time.LocalDate

fun EntryEntity.toDomain(): Entry = Entry(
    id = id,
    title = title,
    body = body,
    entryDate = LocalDate.parse(entryDate),
    source = EntrySource.valueOf(source),
    createdAt = Instant.ofEpochMilli(createdAt),
    updatedAt = Instant.ofEpochMilli(updatedAt),
    isSynced = isSynced,
)

fun Entry.toEntity(): EntryEntity = EntryEntity(
    id = id,
    title = title,
    body = body,
    entryDate = entryDate.toString(),
    source = source.name,
    createdAt = createdAt.toEpochMilli(),
    updatedAt = updatedAt.toEpochMilli(),
    isSynced = isSynced,
)
