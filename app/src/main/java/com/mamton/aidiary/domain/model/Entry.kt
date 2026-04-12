package com.mamton.aidiary.domain.model

import java.time.Instant
import java.time.LocalDate

data class Entry(
    val id: String,
    val title: String,
    val body: String,
    val entryDateStart: LocalDate,
    val entryDateEnd: LocalDate,
    val eventStartAt: Instant? = null,
    val eventEndAt: Instant? = null,
    val originType: OriginType = OriginType.USER_CREATED,
    val source: EntrySource = EntrySource.TEXT,
    val status: EntryStatus = EntryStatus.ACTIVE,
    val currentRevisionId: String? = null,
    val createdAt: Instant,
    val updatedAt: Instant,
    val isSynced: Boolean = false,
) {
    init {
        require(!entryDateStart.isAfter(entryDateEnd)) {
            "entryDateStart must be <= entryDateEnd"
        }
    }
}

enum class EntrySource {
    TEXT,
    VOICE,
    IMPORT,
}
