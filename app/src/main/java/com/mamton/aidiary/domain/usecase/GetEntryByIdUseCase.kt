package com.mamton.aidiary.domain.usecase

import com.mamton.aidiary.domain.model.Entry
import com.mamton.aidiary.domain.repository.EntryRepository
import javax.inject.Inject

class GetEntryByIdUseCase @Inject constructor(
    private val repository: EntryRepository,
) {
    suspend operator fun invoke(id: String): Entry? = repository.getEntryById(id)
}
