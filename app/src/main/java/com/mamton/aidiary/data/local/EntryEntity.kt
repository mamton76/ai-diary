package com.mamton.aidiary.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "entries")
data class EntryEntity(
    @PrimaryKey val id: String,
    val title: String,
    val body: String,
    val entryDate: String,
    val source: String,
    val createdAt: Long,
    val updatedAt: Long,
    val isSynced: Boolean,
)
