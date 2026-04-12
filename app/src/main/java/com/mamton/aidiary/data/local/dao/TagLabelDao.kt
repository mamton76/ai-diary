package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.TagLabelEntity

@Dao
interface TagLabelDao {
    @Insert
    suspend fun insert(label: TagLabelEntity)

    @Query("SELECT * FROM tag_labels WHERE tagId = :tagId ORDER BY isPrimary DESC")
    suspend fun getByTagId(tagId: String): List<TagLabelEntity>

    @Query("SELECT * FROM tag_labels WHERE tagId = :tagId AND isPrimary = 1 LIMIT 1")
    suspend fun getPrimaryByTagId(tagId: String): TagLabelEntity?

    @Query("SELECT * FROM tag_labels WHERE normalizedText LIKE '%' || :query || '%' ORDER BY isPrimary DESC")
    suspend fun searchByNormalizedText(query: String): List<TagLabelEntity>
}
