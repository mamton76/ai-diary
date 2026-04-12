package com.mamton.aidiary.core.di

import android.content.Context
import androidx.room.Room
import com.mamton.aidiary.data.local.DiaryDatabase
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
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): DiaryDatabase =
        Room.databaseBuilder(context, DiaryDatabase::class.java, "diary.db")
            .fallbackToDestructiveMigration(dropAllTables = true)
            .build()

    @Provides
    fun provideEntryDao(db: DiaryDatabase): EntryDao = db.entryDao()

    @Provides
    fun provideEntryRevisionDao(db: DiaryDatabase): EntryRevisionDao = db.entryRevisionDao()

    @Provides
    fun provideTagDao(db: DiaryDatabase): TagDao = db.tagDao()

    @Provides
    fun provideTagLabelDao(db: DiaryDatabase): TagLabelDao = db.tagLabelDao()

    @Provides
    fun provideEntryRevisionTagDao(db: DiaryDatabase): EntryRevisionTagDao = db.entryRevisionTagDao()

    @Provides
    fun provideEntryTagDao(db: DiaryDatabase): EntryTagDao = db.entryTagDao()

    @Provides
    fun provideAssetDao(db: DiaryDatabase): AssetDao = db.assetDao()

    @Provides
    fun provideEntryRevisionAssetDao(db: DiaryDatabase): EntryRevisionAssetDao = db.entryRevisionAssetDao()

    @Provides
    fun provideEntryAssetDao(db: DiaryDatabase): EntryAssetDao = db.entryAssetDao()

    @Provides
    fun provideEntryRevisionSourceLinkDao(db: DiaryDatabase): EntryRevisionSourceLinkDao = db.entryRevisionSourceLinkDao()

    @Provides
    fun provideAIRequestDao(db: DiaryDatabase): AIRequestDao = db.aiRequestDao()

    @Provides
    fun provideAIResultDao(db: DiaryDatabase): AIResultDao = db.aiResultDao()

    @Provides
    fun provideAIFeedbackDao(db: DiaryDatabase): AIFeedbackDao = db.aiFeedbackDao()

    @Provides
    fun provideUserPreferencesDao(db: DiaryDatabase): UserPreferencesDao = db.userPreferencesDao()

    @Provides
    fun provideUserAIContextDao(db: DiaryDatabase): UserAIContextDao = db.userAIContextDao()

    @Provides
    fun provideUserAIContextVersionDao(db: DiaryDatabase): UserAIContextVersionDao = db.userAIContextVersionDao()

    @Provides
    fun provideAIContextSnapshotDao(db: DiaryDatabase): AIContextSnapshotDao = db.aiContextSnapshotDao()
}
