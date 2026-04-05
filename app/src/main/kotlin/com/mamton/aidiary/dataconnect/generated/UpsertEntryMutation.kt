
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



public interface UpsertEntryMutation :
    com.google.firebase.dataconnect.generated.GeneratedMutation<
      DiaryConnector,
      UpsertEntryMutation.Data,
      UpsertEntryMutation.Variables
    >
{
  
    @kotlinx.serialization.Serializable
  public data class Variables(
  
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
  

  
    @kotlinx.serialization.Serializable
  public data class Data(
  
    val entry_upsert: EntryKey
  ) {
    
    
  }
  

  public companion object {
    public val operationName: String = "UpsertEntry"

    public val dataDeserializer: kotlinx.serialization.DeserializationStrategy<Data> =
      kotlinx.serialization.serializer()

    public val variablesSerializer: kotlinx.serialization.SerializationStrategy<Variables> =
      kotlinx.serialization.serializer()
  }
}

public fun UpsertEntryMutation.ref(
  
    id: String,uid: String,title: String,body: String,entryDate: com.google.firebase.dataconnect.LocalDate,source: String,createdAt: com.google.firebase.Timestamp,updatedAt: com.google.firebase.Timestamp,
  
  
): com.google.firebase.dataconnect.MutationRef<
    UpsertEntryMutation.Data,
    UpsertEntryMutation.Variables
  > =
  ref(
    
      UpsertEntryMutation.Variables(
        id=id,uid=uid,title=title,body=body,entryDate=entryDate,source=source,createdAt=createdAt,updatedAt=updatedAt,
  
      )
    
  )

public suspend fun UpsertEntryMutation.execute(
  
    id: String,uid: String,title: String,body: String,entryDate: com.google.firebase.dataconnect.LocalDate,source: String,createdAt: com.google.firebase.Timestamp,updatedAt: com.google.firebase.Timestamp,
  
  
  ): com.google.firebase.dataconnect.MutationResult<
    UpsertEntryMutation.Data,
    UpsertEntryMutation.Variables
  > =
  ref(
    
      id=id,uid=uid,title=title,body=body,entryDate=entryDate,source=source,createdAt=createdAt,updatedAt=updatedAt,
  
    
  ).execute()


