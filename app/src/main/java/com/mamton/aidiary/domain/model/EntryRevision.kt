package com.mamton.aidiary.domain.model

import java.time.Instant
import java.time.LocalDate

data class EntryRevision(
    val id: String,
    val entryId: String,
    val revisionNumber: Int,
    val title: String,
    val body: String,
    val entryDateStart: LocalDate,
    val entryDateEnd: LocalDate,
    val eventStartAt: Instant? = null,
    val eventEndAt: Instant? = null,
    val changeType: RevisionChangeType,
    val createdAt: Instant,
)
