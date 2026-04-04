package com.mamton.aidiary.domain.usecase

import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.repository.EntryRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetEntriesUseCase @Inject constructor(
    private val repository: EntryRepository,
) {
    operator fun invoke(): Flow<List<Entry>> = repository.getEntries()
}
