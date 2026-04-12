package com.mamton.aidiary.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.mamton.aidiary.data.local.dao.AIContextSnapshotDao
import com.mamton.aidiary.data.local.dao.AIFeedbackDao
import com.mamton.aidiary.data.local.dao.AIRequestDao
import com.mamton.aidiary.data.local.dao.AIResultDao
import com.mamton.aidiary.data.local.dao.AssetDao
import com.mamton.aidiary.data.local.dao.EntryAssetDao
import com.mamton.aidiary.data.local.dao.EntryDao
import com.mamton.aidiary.data.local.dao.EntryRevisionAssetDao
import com.mamton.aidiary.data.local.dao.EntryRevisionDao
import com.mamton.aidiary.data.local.dao.EntryRevisionSourceLinkDao
import com.mamton.aidiary.data.local.dao.EntryRevisionTagDao
import com.mamton.aidiary.data.local.dao.EntryTagDao
import com.mamton.aidiary.data.local.dao.TagDao
import com.mamton.aidiary.data.local.dao.TagLabelDao
import com.mamton.aidiary.data.local.dao.UserAIContextDao
import com.mamton.aidiary.data.local.dao.UserAIContextVersionDao
import com.mamton.aidiary.data.local.dao.UserPreferencesDao
import com.mamton.aidiary.data.local.entity.AIContextSnapshotEntity
import com.mamton.aidiary.data.local.entity.AIFeedbackEntity
import com.mamton.aidiary.data.local.entity.AIRequestEntity
import com.mamton.aidiary.data.local.entity.AIResultEntity
import com.mamton.aidiary.data.local.entity.AssetEntity
import com.mamton.aidiary.data.local.entity.EntryAssetEntity
import com.mamton.aidiary.data.local.entity.EntryEntity
import com.mamton.aidiary.data.local.entity.EntryRevisionAssetEntity
import com.mamton.aidiary.data.local.entity.EntryRevisionEntity
import com.mamton.aidiary.data.local.entity.EntryRevisionSourceLinkEntity
import com.mamton.aidiary.data.local.entity.EntryRevisionTagEntity
import com.mamton.aidiary.data.local.entity.EntryTagEntity
import com.mamton.aidiary.data.local.entity.TagEntity
import com.mamton.aidiary.data.local.entity.TagLabelEntity
import com.mamton.aidiary.data.local.entity.UserAIContextEntity
import com.mamton.aidiary.data.local.entity.UserAIContextVersionEntity
import com.mamton.aidiary.data.local.entity.UserPreferencesEntity

@Database(
    entities = [
        EntryEntity::class,
        EntryRevisionEntity::class,
        TagEntity::class,
        TagLabelEntity::class,
        EntryRevisionTagEntity::class,
        EntryTagEntity::class,
        AssetEntity::class,
        EntryRevisionAssetEntity::class,
        EntryAssetEntity::class,
        EntryRevisionSourceLinkEntity::class,
        AIRequestEntity::class,
        AIResultEntity::class,
        AIFeedbackEntity::class,
        UserPreferencesEntity::class,
        UserAIContextEntity::class,
        UserAIContextVersionEntity::class,
        AIContextSnapshotEntity::class,
    ],
    version = 2,
    exportSchema = true,
)
abstract class DiaryDatabase : RoomDatabase() {
    abstract fun entryDao(): EntryDao
    abstract fun entryRevisionDao(): EntryRevisionDao
    abstract fun tagDao(): TagDao
    abstract fun tagLabelDao(): TagLabelDao
    abstract fun entryRevisionTagDao(): EntryRevisionTagDao
    abstract fun entryTagDao(): EntryTagDao
    abstract fun assetDao(): AssetDao
    abstract fun entryRevisionAssetDao(): EntryRevisionAssetDao
    abstract fun entryAssetDao(): EntryAssetDao
    abstract fun entryRevisionSourceLinkDao(): EntryRevisionSourceLinkDao
    abstract fun aiRequestDao(): AIRequestDao
    abstract fun aiResultDao(): AIResultDao
    abstract fun aiFeedbackDao(): AIFeedbackDao
    abstract fun userPreferencesDao(): UserPreferencesDao
    abstract fun userAIContextDao(): UserAIContextDao
    abstract fun userAIContextVersionDao(): UserAIContextVersionDao
    abstract fun aiContextSnapshotDao(): AIContextSnapshotDao
}
