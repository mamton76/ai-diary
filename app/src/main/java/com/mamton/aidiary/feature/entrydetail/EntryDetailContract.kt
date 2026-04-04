package com.mamton.aidiary.feature.entrydetail

import com.mamton.aidiary.domain.model.Entry

data class EntryDetailState(
    val entry: Entry? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val isCreateMode: Boolean = false,
    val titleInput: String = "",
    val bodyInput: String = "",
)

sealed interface EntryDetailEvent {
    data class TitleChanged(val value: String) : EntryDetailEvent
    data class BodyChanged(val value: String) : EntryDetailEvent
    data object SaveEntry : EntryDetailEvent
    data object NavigateBack : EntryDetailEvent
}

sealed interface EntryDetailSideEffect {
    data object NavigateBack : EntryDetailSideEffect
    data class ShowError(val message: String) : EntryDetailSideEffect
}
