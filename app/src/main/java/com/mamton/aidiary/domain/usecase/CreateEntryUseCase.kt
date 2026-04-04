package com.mamton.aidiary.domain.usecase

import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.repository.EntryRepository
import javax.inject.Inject

class CreateEntryUseCase @Inject constructor(
    private val repository: EntryRepository,
) {
    suspend operator fun invoke(title: String, body: String): Entry {
        require(body.isNotBlank()) { "Entry body must not be blank" }
        return repository.createEntry(title, body)
    }
}
