package com.mamton.aidiary.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(
    entities = [EntryEntity::class],
    version = 1,
    exportSchema = true,
)
abstract class DiaryDatabase : RoomDatabase() {
    abstract fun entryDao(): EntryDao
}
