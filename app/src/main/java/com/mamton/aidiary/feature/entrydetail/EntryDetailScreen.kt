package com.mamton.aidiary.feature.entrydetail

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EntryDetailScreen(
    onNavigateBack: () -> Unit,
    viewModel: EntryDetailViewModel = hiltViewModel(),
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.sideEffects.collect { effect ->
            when (effect) {
                EntryDetailSideEffect.NavigateBack -> onNavigateBack()
                is EntryDetailSideEffect.ShowError -> snackbarHostState.showSnackbar(effect.message)
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (state.isCreateMode) "New Entry" else "Entry") },
                navigationIcon = {
                    IconButton(onClick = { viewModel.onEvent(EntryDetailEvent.NavigateBack) }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
            )
        },
        floatingActionButton = {
            if (state.isCreateMode) {
                FloatingActionButton(onClick = { viewModel.onEvent(EntryDetailEvent.SaveEntry) }) {
                    Icon(Icons.Default.Check, contentDescription = "Save")
                }
            }
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
        ) {
            if (state.isCreateMode) {
                OutlinedTextField(
                    value = state.titleInput,
                    onValueChange = { viewModel.onEvent(EntryDetailEvent.TitleChanged(it)) },
                    label = { Text("Title") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )

                OutlinedTextField(
                    value = state.bodyInput,
                    onValueChange = { viewModel.onEvent(EntryDetailEvent.BodyChanged(it)) },
                    label = { Text("What's on your mind?") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .padding(top = 8.dp),
                )
            } else {
                state.entry?.let { entry ->
                    Text(
                        text = entry.title.ifBlank { "Untitled" },
                        style = MaterialTheme.typography.headlineMedium,
                    )
                    Text(
                        text = entry.entryDate.format(DateTimeFormatter.ofPattern("EEEE, MMM d, yyyy")),
                        style = MaterialTheme.typography.labelMedium,
                        modifier = Modifier.padding(top = 4.dp, bottom = 16.dp),
                    )
                    Text(
                        text = entry.body,
                        style = MaterialTheme.typography.bodyLarge,
                    )
                }
            }
        }
    }
}
