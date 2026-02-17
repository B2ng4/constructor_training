<template>
	<q-layout view="lHh lpR fFf" class="base-layout">
		<q-header elevated class="header bg-white text-grey-9">
			<q-toolbar class="toolbar">
				<q-btn
					v-if="$q.screen.lt.md"
					flat
					dense
					round
					icon="menu"
					@click="drawerLeft = !drawerLeft"
				/>
				<router-link to="/personal/home" class="layout-brand row items-center q-mr-xl">
					<q-icon name="school" size="28px" color="primary" />
					<span class="brand-text q-ml-sm">Конструктор тренингов</span>
				</router-link>
				<q-space />
				<UserCard />
			</q-toolbar>
		</q-header>

		<q-drawer
			v-model="drawerLeft"
			show-if-above
			:breakpoint="768"
			side="left"
			bordered
			class="drawer"
			:width="260"
		>
			<div class="drawer-content">
				<router-link
					v-for="nav in navigationButtons"
					:key="nav.url"
					:to="nav.url"
					class="nav-link"
					active-class="nav-link-active"
				>
					<q-item clickable>
						<q-item-section avatar>
							<q-icon :name="nav.icon" :color="$route.path === nav.url ? 'primary' : 'grey-7'" />
						</q-item-section>
						<q-item-section>
							<q-item-label>{{ nav.name }}</q-item-label>
						</q-item-section>
					</q-item>
				</router-link>
			</div>
		</q-drawer>

		<q-page-container class="page-container">
			<router-view />
		</q-page-container>
	</q-layout>
</template>

<script>
import { ref } from "vue";
import UserCard from "@components/features/personal_page/header/UserCard.vue";
import { useUserStore } from "@store/userData.js";

export default {
	name: "BaseLayout",
	components: { UserCard },
	async mounted() {
		const token = localStorage.getItem("tokenAuth");
		if (token && !useUserStore().isLoaded) {
			await useUserStore().fetchUser();
		}
	},
	setup() {
		const drawerLeft = ref(false);
		return {
			drawerLeft,
			navigationButtons: [
				{ name: "Главная", icon: "home", url: "/personal/home" },
				{ name: "Библиотека", icon: "menu_book", url: "/personal/library" },
				{ name: "Мои тренинги", icon: "list_alt", url: "/personal/training" },
				{ name: "Поддержка", icon: "help", url: "/personal/help" },
			],
		};
	},
};
</script>

<style scoped>
.base-layout {
	background: #f5f6fa;
}

.header {
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.toolbar {
	min-height: 56px;
	padding: 0 16px;
}

.layout-brand {
	text-decoration: none;
	color: inherit;
}

.brand-text {
	font-weight: 600;
	font-size: 1.1rem;
	color: #1a1a2e;
}

.drawer {
	background: white;
}

.drawer-content {
	padding-top: 8px;
}

.drawer-header {
	border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.nav-link {
	text-decoration: none;
	color: inherit;
	display: block;
	margin: 2px 12px;
	border-radius: 10px;
}

.nav-link-active .q-item {
	background: rgba(80, 100, 247, 0.1);
	color: #5064f7;
	border-radius: 10px;
}

.nav-link-active .q-item-label {
	font-weight: 500;
}

.page-container {
	background: #f5f6fa;
}
</style>

