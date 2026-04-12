
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
    val entryDateStart: com.google.firebase.dataconnect.LocalDate,
    val entryDateEnd: com.google.firebase.dataconnect.LocalDate,
    val eventStartAt: com.google.firebase.dataconnect.OptionalVariable<@kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp?>,
    val eventEndAt: com.google.firebase.dataconnect.OptionalVariable<@kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp?>,
    val originType: String,
    val source: String,
    val status: String,
    val currentRevisionId: com.google.firebase.dataconnect.OptionalVariable<String?>,
    val createdAt: @kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp,
    val updatedAt: @kotlinx.serialization.Serializable(with = com.google.firebase.dataconnect.serializers.TimestampSerializer::class) com.google.firebase.Timestamp
  ) {
    
    
      
      @kotlin.DslMarker public annotation class BuilderDsl

      @BuilderDsl
      public interface Builder {
        public var id: String
        public var uid: String
        public var title: String
        public var body: String
        public var entryDateStart: com.google.firebase.dataconnect.LocalDate
        public var entryDateEnd: com.google.firebase.dataconnect.LocalDate
        public var eventStartAt: com.google.firebase.Timestamp?
        public var eventEndAt: com.google.firebase.Timestamp?
        public var originType: String
        public var source: String
        public var status: String
        public var currentRevisionId: String?
        public var createdAt: com.google.firebase.Timestamp
        public var updatedAt: com.google.firebase.Timestamp
        
      }

      public companion object {
        @Suppress("NAME_SHADOWING")
        public fun build(
          id: String,uid: String,title: String,body: String,entryDateStart: com.google.firebase.dataconnect.LocalDate,entryDateEnd: com.google.firebase.dataconnect.LocalDate,originType: String,source: String,status: String,createdAt: com.google.firebase.Timestamp,updatedAt: com.google.firebase.Timestamp,
          block_: Builder.() -> Unit
        ): Variables {
          var id= id
            var uid= uid
            var title= title
            var body= body
            var entryDateStart= entryDateStart
            var entryDateEnd= entryDateEnd
            var eventStartAt: com.google.firebase.dataconnect.OptionalVariable<com.google.firebase.Timestamp?> =
                com.google.firebase.dataconnect.OptionalVariable.Undefined
            var eventEndAt: com.google.firebase.dataconnect.OptionalVariable<com.google.firebase.Timestamp?> =
                com.google.firebase.dataconnect.OptionalVariable.Undefined
            var originType= originType
            var source= source
            var status= status
            var currentRevisionId: com.google.firebase.dataconnect.OptionalVariable<String?> =
                com.google.firebase.dataconnect.OptionalVariable.Undefined
            var createdAt= createdAt
            var updatedAt= updatedAt
            

          return object : Builder {
            override var id: String
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { id = value_ }
              
            override var uid: String
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { uid = value_ }
              
            override var title: String
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { title = value_ }
              
            override var body: String
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { body = value_ }
              
            override var entryDateStart: com.google.firebase.dataconnect.LocalDate
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { entryDateStart = value_ }
              
            override var entryDateEnd: com.google.firebase.dataconnect.LocalDate
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { entryDateEnd = value_ }
              
            override var eventStartAt: com.google.firebase.Timestamp?
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { eventStartAt = com.google.firebase.dataconnect.OptionalVariable.Value(value_) }
              
            override var eventEndAt: com.google.firebase.Timestamp?
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { eventEndAt = com.google.firebase.dataconnect.OptionalVariable.Value(value_) }
              
            override var originType: String
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { originType = value_ }
              
            override var source: String
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { source = value_ }
              
            override var status: String
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { status = value_ }
              
            override var currentRevisionId: String?
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { currentRevisionId = com.google.firebase.dataconnect.OptionalVariable.Value(value_) }
              
            override var createdAt: com.google.firebase.Timestamp
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { createdAt = value_ }
              
            override var updatedAt: com.google.firebase.Timestamp
              get() = throw UnsupportedOperationException("getting builder values is not supported")
              set(value_) { updatedAt = value_ }
              
            
          }.apply(block_)
          .let {
            Variables(
              id=id,uid=uid,title=title,body=body,entryDateStart=entryDateStart,entryDateEnd=entryDateEnd,eventStartAt=eventStartAt,eventEndAt=eventEndAt,originType=originType,source=source,status=status,currentRevisionId=currentRevisionId,createdAt=createdAt,updatedAt=updatedAt,
            )
          }
        }
      }
    
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
  
    id: String,uid: String,title: String,body: String,entryDateStart: com.google.firebase.dataconnect.LocalDate,entryDateEnd: com.google.firebase.dataconnect.LocalDate,originType: String,source: String,status: String,createdAt: com.google.firebase.Timestamp,updatedAt: com.google.firebase.Timestamp,
  
    block_: UpsertEntryMutation.Variables.Builder.() -> Unit = {}
  
): com.google.firebase.dataconnect.MutationRef<
    UpsertEntryMutation.Data,
    UpsertEntryMutation.Variables
  > =
  ref(
    
      UpsertEntryMutation.Variables.build(
        id=id,uid=uid,title=title,body=body,entryDateStart=entryDateStart,entryDateEnd=entryDateEnd,originType=originType,source=source,status=status,createdAt=createdAt,updatedAt=updatedAt,
  
    block_
      )
    
  )

public suspend fun UpsertEntryMutation.execute(
  
    id: String,uid: String,title: String,body: String,entryDateStart: com.google.firebase.dataconnect.LocalDate,entryDateEnd: com.google.firebase.dataconnect.LocalDate,originType: String,source: String,status: String,createdAt: com.google.firebase.Timestamp,updatedAt: com.google.firebase.Timestamp,
  
    block_: UpsertEntryMutation.Variables.Builder.() -> Unit = {}
  
  ): com.google.firebase.dataconnect.MutationResult<
    UpsertEntryMutation.Data,
    UpsertEntryMutation.Variables
  > =
  ref(
    
      id=id,uid=uid,title=title,body=body,entryDateStart=entryDateStart,entryDateEnd=entryDateEnd,originType=originType,source=source,status=status,createdAt=createdAt,updatedAt=updatedAt,
  
    block_
    
  ).execute()


