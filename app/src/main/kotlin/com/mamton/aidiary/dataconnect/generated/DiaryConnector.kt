
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

import com.google.firebase.dataconnect.getInstance as _fdcGetInstance
import kotlin.time.Duration.Companion.milliseconds as _milliseconds

public interface DiaryConnector : com.google.firebase.dataconnect.generated.GeneratedConnector<DiaryConnector> {
  override val dataConnect: com.google.firebase.dataconnect.FirebaseDataConnect

  
    public val getEntryById: GetEntryByIdQuery
  
    public val listEntriesByUser: ListEntriesByUserQuery
  
    public val upsertEntry: UpsertEntryMutation
  

  public companion object {
    @Suppress("MemberVisibilityCanBePrivate")
    public val config: com.google.firebase.dataconnect.ConnectorConfig = com.google.firebase.dataconnect.ConnectorConfig(
      connector = "diary",
      location = "europe-west8",
      serviceId = "ai-diary-a3799-service",
    )

    public fun getInstance(
      dataConnect: com.google.firebase.dataconnect.FirebaseDataConnect
    ):DiaryConnector = synchronized(instances) {
      instances.getOrPut(dataConnect) {
        DiaryConnectorImpl(dataConnect)
      }
    }

    private val instances = java.util.WeakHashMap<com.google.firebase.dataconnect.FirebaseDataConnect, DiaryConnectorImpl>()

    
  }
}

public val DiaryConnector.Companion.instance:DiaryConnector
  get() = getInstance(com.google.firebase.dataconnect.FirebaseDataConnect._fdcGetInstance(
    config
  ))

public fun DiaryConnector.Companion.getInstance(
  settings: com.google.firebase.dataconnect.DataConnectSettings = com.google.firebase.dataconnect.DataConnectSettings()
):DiaryConnector =
  getInstance(com.google.firebase.dataconnect.FirebaseDataConnect._fdcGetInstance(config, settings))

public fun DiaryConnector.Companion.getInstance(
  app: com.google.firebase.FirebaseApp,
  settings: com.google.firebase.dataconnect.DataConnectSettings = com.google.firebase.dataconnect.DataConnectSettings()
):DiaryConnector =
  getInstance(com.google.firebase.dataconnect.FirebaseDataConnect._fdcGetInstance(app, config, settings))

private class DiaryConnectorImpl(
  override val dataConnect: com.google.firebase.dataconnect.FirebaseDataConnect
) : DiaryConnector {
  
    override val getEntryById by lazy(LazyThreadSafetyMode.PUBLICATION) {
      GetEntryByIdQueryImpl(this)
    }
  
    override val listEntriesByUser by lazy(LazyThreadSafetyMode.PUBLICATION) {
      ListEntriesByUserQueryImpl(this)
    }
  
    override val upsertEntry by lazy(LazyThreadSafetyMode.PUBLICATION) {
      UpsertEntryMutationImpl(this)
    }
  

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun operations(): List<com.google.firebase.dataconnect.generated.GeneratedOperation<DiaryConnector, *, *>> =
    queries() + mutations()

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun mutations(): List<com.google.firebase.dataconnect.generated.GeneratedMutation<DiaryConnector, *, *>> =
    listOf(
      upsertEntry,
        
    )

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun queries(): List<com.google.firebase.dataconnect.generated.GeneratedQuery<DiaryConnector, *, *>> =
    listOf(
      getEntryById,
        listEntriesByUser,
        
    )

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun copy(dataConnect: com.google.firebase.dataconnect.FirebaseDataConnect) =
    DiaryConnectorImpl(dataConnect)

  override fun equals(other: Any?): Boolean =
    other is DiaryConnectorImpl &&
    other.dataConnect == dataConnect

  override fun hashCode(): Int =
    java.util.Objects.hash(
      "DiaryConnectorImpl",
      dataConnect,
    )

  override fun toString(): String =
    "DiaryConnectorImpl(dataConnect=$dataConnect)"
}



private open class DiaryConnectorGeneratedQueryImpl<Data, Variables>(
  override val connector: DiaryConnector,
  override val operationName: String,
  override val dataDeserializer: kotlinx.serialization.DeserializationStrategy<Data>,
  override val variablesSerializer: kotlinx.serialization.SerializationStrategy<Variables>,
) : com.google.firebase.dataconnect.generated.GeneratedQuery<DiaryConnector, Data, Variables> {

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun copy(
    connector: DiaryConnector,
    operationName: String,
    dataDeserializer: kotlinx.serialization.DeserializationStrategy<Data>,
    variablesSerializer: kotlinx.serialization.SerializationStrategy<Variables>,
  ) =
    DiaryConnectorGeneratedQueryImpl(
      connector, operationName, dataDeserializer, variablesSerializer
    )

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun <NewVariables> withVariablesSerializer(
    variablesSerializer: kotlinx.serialization.SerializationStrategy<NewVariables>
  ) =
    DiaryConnectorGeneratedQueryImpl(
      connector, operationName, dataDeserializer, variablesSerializer
    )

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun <NewData> withDataDeserializer(
    dataDeserializer: kotlinx.serialization.DeserializationStrategy<NewData>
  ) =
    DiaryConnectorGeneratedQueryImpl(
      connector, operationName, dataDeserializer, variablesSerializer
    )

  override fun equals(other: Any?): Boolean =
    other is DiaryConnectorGeneratedQueryImpl<*,*> &&
    other.connector == connector &&
    other.operationName == operationName &&
    other.dataDeserializer == dataDeserializer &&
    other.variablesSerializer == variablesSerializer

  override fun hashCode(): Int =
    java.util.Objects.hash(
      "DiaryConnectorGeneratedQueryImpl",
      connector, operationName, dataDeserializer, variablesSerializer
    )

  override fun toString(): String =
    "DiaryConnectorGeneratedQueryImpl(" +
    "operationName=$operationName, " +
    "dataDeserializer=$dataDeserializer, " +
    "variablesSerializer=$variablesSerializer, " +
    "connector=$connector)"
}

private open class DiaryConnectorGeneratedMutationImpl<Data, Variables>(
  override val connector: DiaryConnector,
  override val operationName: String,
  override val dataDeserializer: kotlinx.serialization.DeserializationStrategy<Data>,
  override val variablesSerializer: kotlinx.serialization.SerializationStrategy<Variables>,
) : com.google.firebase.dataconnect.generated.GeneratedMutation<DiaryConnector, Data, Variables> {

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun copy(
    connector: DiaryConnector,
    operationName: String,
    dataDeserializer: kotlinx.serialization.DeserializationStrategy<Data>,
    variablesSerializer: kotlinx.serialization.SerializationStrategy<Variables>,
  ) =
    DiaryConnectorGeneratedMutationImpl(
      connector, operationName, dataDeserializer, variablesSerializer
    )

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun <NewVariables> withVariablesSerializer(
    variablesSerializer: kotlinx.serialization.SerializationStrategy<NewVariables>
  ) =
    DiaryConnectorGeneratedMutationImpl(
      connector, operationName, dataDeserializer, variablesSerializer
    )

  @com.google.firebase.dataconnect.ExperimentalFirebaseDataConnect
  override fun <NewData> withDataDeserializer(
    dataDeserializer: kotlinx.serialization.DeserializationStrategy<NewData>
  ) =
    DiaryConnectorGeneratedMutationImpl(
      connector, operationName, dataDeserializer, variablesSerializer
    )

  override fun equals(other: Any?): Boolean =
    other is DiaryConnectorGeneratedMutationImpl<*,*> &&
    other.connector == connector &&
    other.operationName == operationName &&
    other.dataDeserializer == dataDeserializer &&
    other.variablesSerializer == variablesSerializer

  override fun hashCode(): Int =
    java.util.Objects.hash(
      "DiaryConnectorGeneratedMutationImpl",
      connector, operationName, dataDeserializer, variablesSerializer
    )

  override fun toString(): String =
    "DiaryConnectorGeneratedMutationImpl(" +
    "operationName=$operationName, " +
    "dataDeserializer=$dataDeserializer, " +
    "variablesSerializer=$variablesSerializer, " +
    "connector=$connector)"
}



private class GetEntryByIdQueryImpl(
  connector: DiaryConnector
):
  GetEntryByIdQuery,
  DiaryConnectorGeneratedQueryImpl<
      GetEntryByIdQuery.Data,
      GetEntryByIdQuery.Variables
  >(
    connector,
    GetEntryByIdQuery.Companion.operationName,
    GetEntryByIdQuery.Companion.dataDeserializer,
    GetEntryByIdQuery.Companion.variablesSerializer,
  )


private class ListEntriesByUserQueryImpl(
  connector: DiaryConnector
):
  ListEntriesByUserQuery,
  DiaryConnectorGeneratedQueryImpl<
      ListEntriesByUserQuery.Data,
      ListEntriesByUserQuery.Variables
  >(
    connector,
    ListEntriesByUserQuery.Companion.operationName,
    ListEntriesByUserQuery.Companion.dataDeserializer,
    ListEntriesByUserQuery.Companion.variablesSerializer,
  )


private class UpsertEntryMutationImpl(
  connector: DiaryConnector
):
  UpsertEntryMutation,
  DiaryConnectorGeneratedMutationImpl<
      UpsertEntryMutation.Data,
      UpsertEntryMutation.Variables
  >(
    connector,
    UpsertEntryMutation.Companion.operationName,
    UpsertEntryMutation.Companion.dataDeserializer,
    UpsertEntryMutation.Companion.variablesSerializer,
  )


