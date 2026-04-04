package com.mamton.aidiary.domain.model

import java.time.Instant
import java.time.LocalDate

data class Entry(
    val id: String,
    val title: String,
    val body: String,
    val entryDate: LocalDate,
    val source: EntrySource = EntrySource.TEXT,
    val createdAt: Instant,
    val updatedAt: Instant,
    val isSynced: Boolean = false,
)

enum class EntrySource {
    TEXT,
    VOICE,
    IMPORT,
}
