package com.mamton.aidiary.core.di

import android.content.Context
import androidx.room.Room
import com.mamton.aidiary.data.local.DiaryDatabase
import com.mamton.aidiary.data.local.EntryDao
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
            .fallbackToDestructiveMigration()
            .build()

    @Provides
    fun provideEntryDao(database: DiaryDatabase): EntryDao =
        database.entryDao()
}
