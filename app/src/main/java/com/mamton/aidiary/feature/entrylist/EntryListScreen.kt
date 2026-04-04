package com.mamton.aidiary.feature.entrylist

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.mamton.aidiary.domain.model.Entry
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EntryListScreen(
    onNavigateToDetail: (String) -> Unit,
    onNavigateToCreate: () -> Unit,
    viewModel: EntryListViewModel = hiltViewModel(),
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.sideEffects.collect { effect ->
            when (effect) {
                is EntryListSideEffect.NavigateToDetail -> onNavigateToDetail(effect.id)
                EntryListSideEffect.NavigateToCreate -> onNavigateToCreate()
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Diary") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { viewModel.onEvent(EntryListEvent.CreateNewEntry) }) {
                Icon(Icons.Default.Add, contentDescription = "New entry")
            }
        },
    ) { padding ->
        PullToRefreshBox(
            isRefreshing = state.isLoading,
            onRefresh = { viewModel.onEvent(EntryListEvent.Refresh) },
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
        ) {
            when {
                state.error != null -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text(
                            text = state.error ?: "Unknown error",
                            color = MaterialTheme.colorScheme.error,
                        )
                    }
                }
                state.entries.isEmpty() && !state.isLoading -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("No entries yet. Tap + to create one.")
                    }
                }
                else -> {
                    LazyColumn(Modifier.fillMaxSize()) {
                        items(state.entries, key = { it.id }) { entry ->
                            EntryItem(
                                entry = entry,
                                onClick = { viewModel.onEvent(EntryListEvent.EntryClicked(entry.id)) },
                            )
                        }
                    }
                }
            }
        }
    }
}

private val dateFormatter = DateTimeFormatter.ofPattern("MMM d, yyyy")

@Composable
private fun EntryItem(entry: Entry, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp)
            .clickable(onClick = onClick),
    ) {
        Column(Modifier.padding(16.dp)) {
            Text(
                text = entry.title.ifBlank { "Untitled" },
                style = MaterialTheme.typography.titleMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = entry.body,
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.padding(top = 4.dp),
            )
            Text(
                text = entry.entryDate.format(dateFormatter),
                style = MaterialTheme.typography.labelSmall,
                modifier = Modifier.padding(top = 8.dp),
            )
        }
    }
}
