
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


public interface GetEntryByIdQuery :
    com.google.firebase.dataconnect.generated.GeneratedQuery<
      DiaryConnector,
      GetEntryByIdQuery.Data,
      GetEntryByIdQuery.Variables
    >
{
  
    @kotlinx.serialization.Serializable
  public data class Variables(
  
    val id: String
  ) {
    
    
  }
  

  
    @kotlinx.serialization.Serializable
  public data class Data(
  
    val entry: Entry?
  ) {
    
      
        @kotlinx.serialization.Serializable
  public data class Entry(
  
    val id: String,
    val uid: String,
    val title: String,
    val body: String,
    val entryDateStart: com.google.firebase.dataconnect.LocalDate,
    val entryDateEnd: com.google.firebase.dataconnect.LocalDate,
    val eventStartAt: @kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp?,
    val eventEndAt: @kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp?,
    val originType: String,
    val source: String,
    val status: String,
    val currentRevisionId: String?,
    val createdAt: @kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp,
    val updatedAt: @kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp
  ) {
    
    
  }
      
    
    
  }
  

  public companion object {
    public val operationName: String = "GetEntryById"

    public val dataDeserializer: kotlinx.serialization.DeserializationStrategy<Data> =
      kotlinx.serialization.serializer()

    public val variablesSerializer: kotlinx.serialization.SerializationStrategy<Variables> =
      kotlinx.serialization.serializer()
  }
}

public fun GetEntryByIdQuery.ref(
  
    id: String,
  
  
): com.google.firebase.dataconnect.QueryRef<
    GetEntryByIdQuery.Data,
    GetEntryByIdQuery.Variables
  > =
  ref(
    
      GetEntryByIdQuery.Variables(
        id=id,
  
      )
    
  )

public suspend fun GetEntryByIdQuery.execute(
  
    id: String,
  
  
  ): com.google.firebase.dataconnect.QueryResult<
    GetEntryByIdQuery.Data,
    GetEntryByIdQuery.Variables
  > =
  ref(
    
      id=id,
  
    
  ).execute()


  public fun GetEntryByIdQuery.flow(
    
      id: String,
  
    
    ): kotlinx.coroutines.flow.Flow<GetEntryByIdQuery.Data> =
    ref(
        
          id=id,
  
        
      ).subscribe()
      .flow
      ._flow_map { querySubscriptionResult -> querySubscriptionResult.result.getOrNull() }
      ._flow_filterNotNull()
      ._flow_map { it.data }

