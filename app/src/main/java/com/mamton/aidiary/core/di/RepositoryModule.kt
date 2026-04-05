package com.mamton.aidiary.core.di

import com.mamton.aidiary.data.remote.EntryRemoteDataSource
import com.mamton.aidiary.data.repository.EntryRepositoryImpl
import com.mamton.aidiary.domain.repository.EntryRepository
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindEntryRepository(impl: EntryRepositoryImpl): EntryRepository

    companion object {
        @Provides
        @Singleton
        fun provideEntryRemoteDataSource(): EntryRemoteDataSource = EntryRemoteDataSource()
    }
}
