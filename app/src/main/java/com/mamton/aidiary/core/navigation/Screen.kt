package com.mamton.aidiary.core.navigation

sealed interface Screen {
    val route: String

    data object Auth : Screen {
        override val route = "auth"
    }

    data object EntryList : Screen {
        override val route = "entry_list"
    }

    data object EntryDetail : Screen {
        const val ARG_ENTRY_ID = "entryId"
        override val route = "entry_detail?$ARG_ENTRY_ID={$ARG_ENTRY_ID}"

        fun createRoute(entryId: String? = null): String =
            if (entryId != null) "entry_detail?$ARG_ENTRY_ID=$entryId"
            else "entry_detail"
    }
}
