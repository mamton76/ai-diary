package com.mamton.aidiary.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface EntryDao {
    @Query("SELECT * FROM entries ORDER BY entryDate DESC, createdAt DESC")
    fun observeAll(): Flow<List<EntryEntity>>

    @Query("SELECT * FROM entries WHERE id = :id")
    suspend fun getById(id: String): EntryEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(entry: EntryEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(entries: List<EntryEntity>)

    @Query("SELECT * FROM entries WHERE isSynced = 0")
    suspend fun getUnsynced(): List<EntryEntity>

    @Query("UPDATE entries SET isSynced = 1 WHERE id = :id")
    suspend fun markSynced(id: String)
}
