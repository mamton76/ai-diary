package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.EntryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface EntryDao {
    @Query("SELECT * FROM entries WHERE status != 'DELETED' ORDER BY entryDateStart DESC, createdAt DESC")
    fun observeAll(): Flow<List<EntryEntity>>

    @Query("SELECT * FROM entries WHERE entryDateStart >= :start AND entryDateEnd <= :end AND status != 'DELETED' ORDER BY entryDateStart DESC, createdAt DESC")
    fun observeByDateRange(start: String, end: String): Flow<List<EntryEntity>>

    @Query("SELECT * FROM entries WHERE status = :status ORDER BY entryDateStart DESC, createdAt DESC")
    fun observeByStatus(status: String): Flow<List<EntryEntity>>

    @Query("SELECT * FROM entries WHERE originType = :originType AND status != 'DELETED' ORDER BY entryDateStart DESC, createdAt DESC")
    fun observeByOriginType(originType: String): Flow<List<EntryEntity>>

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
