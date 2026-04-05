package com.mamton.aidiary.core.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.google.firebase.auth.FirebaseAuth
import com.mamton.aidiary.feature.auth.AuthScreen
import com.mamton.aidiary.feature.entrydetail.EntryDetailScreen
import com.mamton.aidiary.feature.entrylist.EntryListScreen

@Composable
fun DiaryNavHost() {
    val navController = rememberNavController()
    val isSignedIn = FirebaseAuth.getInstance().currentUser != null

    val startDestination = if (isSignedIn) Screen.EntryList.route else Screen.Auth.route

    NavHost(
        navController = navController,
        startDestination = startDestination,
    ) {
        composable(Screen.Auth.route) {
            AuthScreen(
                onSignedIn = {
                    navController.navigate(Screen.EntryList.route) {
                        popUpTo(Screen.Auth.route) { inclusive = true }
                    }
                },
            )
        }

        composable(Screen.EntryList.route) {
            EntryListScreen(
                onNavigateToDetail = { id ->
                    navController.navigate(Screen.EntryDetail.createRoute(id))
                },
                onNavigateToCreate = {
                    navController.navigate(Screen.EntryDetail.createRoute())
                },
            )
        }

        composable(
            route = Screen.EntryDetail.route,
            arguments = listOf(
                navArgument(Screen.EntryDetail.ARG_ENTRY_ID) {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                },
            ),
        ) {
            EntryDetailScreen(
                onNavigateBack = { navController.popBackStack() },
            )
        }
    }
}
