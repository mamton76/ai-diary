package com.mamton.aidiary.data.mapper

import com.mamton.aidiary.data.local.entity.TagEntity
import com.mamton.aidiary.data.local.entity.TagLabelEntity
import com.mamton.aidiary.domain.model.Tag
import com.mamton.aidiary.domain.model.TagLabel
import com.mamton.aidiary.domain.model.TagSource
import com.mamton.aidiary.domain.model.TagType
import java.time.Instant

fun TagEntity.toDomain(): Tag = Tag(
    id = id,
    userId = userId,
    type = type?.let { runCatching { TagType.valueOf(it) }.getOrNull() },
    source = runCatching { TagSource.valueOf(source) }.getOrDefault(TagSource.USER),
    mergedIntoTagId = mergedIntoTagId,
    createdAt = Instant.ofEpochMilli(createdAt),
    updatedAt = Instant.ofEpochMilli(updatedAt),
)

fun Tag.toEntity(): TagEntity = TagEntity(
    id = id,
    userId = userId,
    type = type?.name,
    source = source.name,
    mergedIntoTagId = mergedIntoTagId,
    createdAt = createdAt.toEpochMilli(),
    updatedAt = updatedAt.toEpochMilli(),
)

fun TagLabelEntity.toDomain(): TagLabel = TagLabel(
    id = id,
    tagId = tagId,
    text = text,
    normalizedText = normalizedText,
    isPrimary = isPrimary,
    locale = locale,
    source = runCatching { TagSource.valueOf(source) }.getOrDefault(TagSource.USER),
    createdAt = Instant.ofEpochMilli(createdAt),
    updatedAt = Instant.ofEpochMilli(updatedAt),
)

fun TagLabel.toEntity(): TagLabelEntity = TagLabelEntity(
    id = id,
    tagId = tagId,
    text = text,
    normalizedText = normalizedText,
    isPrimary = isPrimary,
    locale = locale,
    source = source.name,
    createdAt = createdAt.toEpochMilli(),
    updatedAt = updatedAt.toEpochMilli(),
)
