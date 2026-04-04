package com.mamton.aidiary.domain.usecase

import com.mamton.aidiary.domain.repository.EntryRepository
import javax.inject.Inject

class SyncEntriesUseCase @Inject constructor(
    private val repository: EntryRepository,
) {
    suspend operator fun invoke() = repository.syncEntries()
}
