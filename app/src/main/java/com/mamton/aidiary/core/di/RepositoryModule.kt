package com.mamton.aidiary.core.di

import com.mamton.aidiary.data.repository.EntryRepositoryImpl
import com.mamton.aidiary.domain.repository.EntryRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindEntryRepository(impl: EntryRepositoryImpl): EntryRepository
}
