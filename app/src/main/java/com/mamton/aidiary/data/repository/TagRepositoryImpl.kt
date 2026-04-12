package com.mamton.aidiary.data.repository

import com.mamton.aidiary.data.local.dao.EntryTagDao
import com.mamton.aidiary.data.local.dao.TagDao
import com.mamton.aidiary.data.local.dao.TagLabelDao
import com.mamton.aidiary.data.local.entity.EntryTagEntity
import com.mamton.aidiary.data.mapper.toDomain
import com.mamton.aidiary.data.mapper.toEntity
import com.mamton.aidiary.domain.model.Tag
import com.mamton.aidiary.domain.model.TagLabel
import com.mamton.aidiary.domain.model.TagSource
import com.mamton.aidiary.domain.model.TagType
import com.mamton.aidiary.domain.repository.TagRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.time.Instant
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TagRepositoryImpl @Inject constructor(
    private val tagDao: TagDao,
    private val tagLabelDao: TagLabelDao,
    private val entryTagDao: EntryTagDao,
) : TagRepository {

    override suspend fun createTag(
        userId: String,
        text: String,
        type: TagType?,
        source: TagSource,
    ): Tag {
        val now = Instant.now()
        val tag = Tag(
            id = UUID.randomUUID().toString(),
            userId = userId,
            type = type,
            source = source,
            createdAt = now,
            updatedAt = now,
        )
        tagDao.insert(tag.toEntity())

        val label = TagLabel(
            id = UUID.randomUUID().toString(),
            tagId = tag.id,
            text = text,
            normalizedText = text.trim().lowercase(),
            isPrimary = true,
            source = source,
            createdAt = now,
            updatedAt = now,
        )
        tagLabelDao.insert(label.toEntity())

        return tag
    }

    override fun getActiveTags(userId: String): Flow<List<Tag>> =
        tagDao.observeActiveTags(userId).map { entities -> entities.map { it.toDomain() } }

    override suspend fun addTagToEntry(entryId: String, tagId: String) {
        entryTagDao.insert(EntryTagEntity(entryId = entryId, tagId = tagId))
    }

    override suspend fun removeTagFromEntry(entryId: String, tagId: String) {
        entryTagDao.delete(entryId, tagId)
    }

    override suspend fun getTagIdsForEntry(entryId: String): List<String> =
        entryTagDao.getTagIdsForEntry(entryId)

    override suspend fun searchTags(query: String): List<TagLabel> =
        tagLabelDao.searchByNormalizedText(query.trim().lowercase()).map { it.toDomain() }
}
