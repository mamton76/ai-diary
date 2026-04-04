package com.mamton.aidiary.core.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.mamton.aidiary.feature.entrydetail.EntryDetailScreen
import com.mamton.aidiary.feature.entrylist.EntryListScreen

@Composable
fun DiaryNavHost() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Screen.EntryList.route,
    ) {
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
