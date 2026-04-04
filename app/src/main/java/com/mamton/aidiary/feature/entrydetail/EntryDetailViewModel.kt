package com.mamton.aidiary.feature.entrydetail

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mamton.aidiary.core.navigation.Screen
import com.mamton.aidiary.domain.usecase.CreateEntryUseCase
import com.mamton.aidiary.domain.usecase.GetEntryByIdUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class EntryDetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val getEntryById: GetEntryByIdUseCase,
    private val createEntry: CreateEntryUseCase,
) : ViewModel() {

    private val entryId: String? = savedStateHandle[Screen.EntryDetail.ARG_ENTRY_ID]

    private val _state = MutableStateFlow(EntryDetailState(isCreateMode = entryId == null))
    val state: StateFlow<EntryDetailState> = _state.asStateFlow()

    private val _sideEffects = Channel<EntryDetailSideEffect>(Channel.BUFFERED)
    val sideEffects = _sideEffects.receiveAsFlow()

    init {
        if (entryId != null) loadEntry(entryId)
    }

    fun onEvent(event: EntryDetailEvent) {
        when (event) {
            is EntryDetailEvent.TitleChanged -> _state.update { it.copy(titleInput = event.value) }
            is EntryDetailEvent.BodyChanged -> _state.update { it.copy(bodyInput = event.value) }
            EntryDetailEvent.SaveEntry -> save()
            EntryDetailEvent.NavigateBack -> {
                viewModelScope.launch { _sideEffects.send(EntryDetailSideEffect.NavigateBack) }
            }
        }
    }

    private fun loadEntry(id: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val entry = getEntryById(id)
                _state.update {
                    it.copy(
                        entry = entry,
                        titleInput = entry?.title.orEmpty(),
                        bodyInput = entry?.body.orEmpty(),
                        isLoading = false,
                    )
                }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }

    private fun save() {
        val currentState = _state.value
        if (currentState.bodyInput.isBlank()) {
            viewModelScope.launch {
                _sideEffects.send(EntryDetailSideEffect.ShowError("Entry body cannot be empty"))
            }
            return
        }

        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                createEntry(currentState.titleInput, currentState.bodyInput)
                _sideEffects.send(EntryDetailSideEffect.NavigateBack)
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }
}
