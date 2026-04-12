package com.mamton.aidiary.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.mamton.aidiary.data.local.entity.UserPreferencesEntity

@Dao
interface UserPreferencesDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(prefs: UserPreferencesEntity)

    @Query("SELECT * FROM user_preferences WHERE userId = :userId")
    suspend fun getByUserId(userId: String): UserPreferencesEntity?
}
