package com.mamton.aidiary.domain.repository

import com.mamton.aidiary.domain.model.Tag
import com.mamton.aidiary.domain.model.TagLabel
import com.mamton.aidiary.domain.model.TagSource
import com.mamton.aidiary.domain.model.TagType
import kotlinx.coroutines.flow.Flow

interface TagRepository {
    suspend fun createTag(userId: String, text: String, type: TagType? = null, source: TagSource = TagSource.USER): Tag
    fun getActiveTags(userId: String): Flow<List<Tag>>
    suspend fun addTagToEntry(entryId: String, tagId: String)
    suspend fun removeTagFromEntry(entryId: String, tagId: String)
    suspend fun getTagIdsForEntry(entryId: String): List<String>
    suspend fun searchTags(query: String): List<TagLabel>
}
