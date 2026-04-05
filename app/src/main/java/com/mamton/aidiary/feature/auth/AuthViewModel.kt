package com.mamton.aidiary.feature.auth

import android.content.Context
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.GoogleAuthProvider
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val firebaseAuth: FirebaseAuth,
) : ViewModel() {

    private val _state = MutableStateFlow(AuthState())
    val state: StateFlow<AuthState> = _state.asStateFlow()

    private val _sideEffects = Channel<AuthSideEffect>(Channel.BUFFERED)
    val sideEffects = _sideEffects.receiveAsFlow()

    init {
        if (firebaseAuth.currentUser != null) {
            _state.update { it.copy(isSignedIn = true) }
            viewModelScope.launch { _sideEffects.send(AuthSideEffect.NavigateToEntryList) }
        }
    }

    fun onEvent(event: AuthEvent) {
        when (event) {
            AuthEvent.SignInClicked -> { /* triggered via signInWithGoogle(context) */ }
            AuthEvent.DismissError -> _state.update { it.copy(error = null) }
        }
    }

    fun signInWithGoogle(context: Context) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            try {
                val credentialManager = CredentialManager.create(context)

                val googleIdOption = GetGoogleIdOption.Builder()
                    .setFilterByAuthorizedAccounts(false)
                    .setServerClientId(WEB_CLIENT_ID)
                    .build()

                val request = GetCredentialRequest.Builder()
                    .addCredentialOption(googleIdOption)
                    .build()

                val result = credentialManager.getCredential(context, request)
                val credential = result.credential

                if (credential is CustomCredential &&
                    credential.type == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL
                ) {
                    val googleIdTokenCredential = GoogleIdTokenCredential.createFrom(credential.data)
                    val firebaseCredential = GoogleAuthProvider.getCredential(
                        googleIdTokenCredential.idToken, null
                    )
                    firebaseAuth.signInWithCredential(firebaseCredential).await()

                    _state.update { it.copy(isSignedIn = true, isLoading = false) }
                    _sideEffects.send(AuthSideEffect.NavigateToEntryList)
                } else {
                    _state.update { it.copy(error = "Unexpected credential type", isLoading = false) }
                }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message ?: "Sign-in failed", isLoading = false) }
            }
        }
    }

    companion object {
        private const val WEB_CLIENT_ID =
            "335452858649-m64sgf5l91mt9mlbm4300ju9pe1fjmso.apps.googleusercontent.com"
    }
}
