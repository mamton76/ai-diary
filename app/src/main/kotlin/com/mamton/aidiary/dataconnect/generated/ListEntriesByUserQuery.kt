
@file:Suppress(
  "KotlinRedundantDiagnosticSuppress",
  "LocalVariableName",
  "MayBeConstant",
  "RedundantVisibilityModifier",
  "RedundantCompanionReference",
  "RemoveEmptyClassBody",
  "SpellCheckingInspection",
  "LocalVariableName",
  "unused",
)

package com.mamton.aidiary.dataconnect.generated


import kotlinx.coroutines.flow.filterNotNull as _flow_filterNotNull
import kotlinx.coroutines.flow.map as _flow_map


public interface ListEntriesByUserQuery :
    com.google.firebase.dataconnect.generated.GeneratedQuery<
      DiaryConnector,
      ListEntriesByUserQuery.Data,
      ListEntriesByUserQuery.Variables
    >
{
  
    @kotlinx.serialization.Serializable
  public data class Variables(
  
    val uid: String
  ) {
    
    
  }
  

  
    @kotlinx.serialization.Serializable
  public data class Data(
  
    val entries: List<EntriesItem>
  ) {
    
      
        @kotlinx.serialization.Serializable
  public data class EntriesItem(
  
    val id: String,
    val uid: String,
    val title: String,
    val body: String,
    val entryDate: com.google.firebase.dataconnect.LocalDate,
    val source: String,
    val createdAt: @kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp,
    val updatedAt: @kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp
  ) {
    
    
  }
      
    
    
  }
  

  public companion object {
    public val operationName: String = "ListEntriesByUser"

    public val dataDeserializer: kotlinx.serialization.DeserializationStrategy<Data> =
      kotlinx.serialization.serializer()

    public val variablesSerializer: kotlinx.serialization.SerializationStrategy<Variables> =
      kotlinx.serialization.serializer()
  }
}

public fun ListEntriesByUserQuery.ref(
  
    uid: String,
  
  
): com.google.firebase.dataconnect.QueryRef<
    ListEntriesByUserQuery.Data,
    ListEntriesByUserQuery.Variables
  > =
  ref(
    
      ListEntriesByUserQuery.Variables(
        uid=uid,
  
      )
    
  )

public suspend fun ListEntriesByUserQuery.execute(
  
    uid: String,
  
  
  ): com.google.firebase.dataconnect.QueryResult<
    ListEntriesByUserQuery.Data,
    ListEntriesByUserQuery.Variables
  > =
  ref(
    
      uid=uid,
  
    
  ).execute()


  public fun ListEntriesByUserQuery.flow(
    
      uid: String,
  
    
    ): kotlinx.coroutines.flow.Flow<ListEntriesByUserQuery.Data> =
    ref(
        
          uid=uid,
  
        
      ).subscribe()
      .flow
      ._flow_map { querySubscriptionResult -> querySubscriptionResult.result.getOrNull() }
      ._flow_filterNotNull()
      ._flow_map { it.data }

