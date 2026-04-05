package com.mamton.aidiary.feature.auth

data class AuthState(
    val isLoading: Boolean = false,
    val isSignedIn: Boolean = false,
    val error: String? = null,
)

sealed interface AuthEvent {
    data object SignInClicked : AuthEvent
    data object DismissError : AuthEvent
}

sealed interface AuthSideEffect {
    data object NavigateToEntryList : AuthSideEffect
}
