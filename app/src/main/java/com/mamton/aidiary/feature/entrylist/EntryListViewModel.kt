package com.mamton.aidiary.feature.entrylist

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mamton.aidiary.domain.usecase.GetEntriesUseCase
import com.mamton.aidiary.domain.usecase.SyncEntriesUseCase
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
class EntryListViewModel @Inject constructor(
    private val getEntries: GetEntriesUseCase,
    private val syncEntries: SyncEntriesUseCase,
) : ViewModel() {

    private val _state = MutableStateFlow(EntryListState())
    val state: StateFlow<EntryListState> = _state.asStateFlow()

    private val _sideEffects = Channel<EntryListSideEffect>(Channel.BUFFERED)
    val sideEffects = _sideEffects.receiveAsFlow()

    init {
        observeEntries()
        sync()
    }

    fun onEvent(event: EntryListEvent) {
        when (event) {
            EntryListEvent.Refresh -> sync()
            EntryListEvent.CreateNewEntry -> {
                viewModelScope.launch {
                    _sideEffects.send(EntryListSideEffect.NavigateToCreate)
                }
            }
            is EntryListEvent.EntryClicked -> {
                viewModelScope.launch {
                    _sideEffects.send(EntryListSideEffect.NavigateToDetail(event.id))
                }
            }
        }
    }

    private fun observeEntries() {
        viewModelScope.launch {
            getEntries().collect { entries ->
                _state.update { it.copy(entries = entries, isLoading = false) }
            }
        }
    }

    private fun sync() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                syncEntries()
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message) }
            } finally {
                _state.update { it.copy(isLoading = false) }
            }
        }
    }
}
