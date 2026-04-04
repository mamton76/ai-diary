package com.mamton.aidiary.feature.entrylist

import com.mamton.aidiary.domain.model.Entry

data class EntryListState(
    val entries: List<Entry> = emptyList(),
    val isLoading: Boolean = true,
    val error: String? = null,
)

sealed interface EntryListEvent {
    data object Refresh : EntryListEvent
    data object CreateNewEntry : EntryListEvent
    data class EntryClicked(val id: String) : EntryListEvent
}

sealed interface EntryListSideEffect {
    data class NavigateToDetail(val id: String) : EntryListSideEffect
    data object NavigateToCreate : EntryListSideEffect
}
