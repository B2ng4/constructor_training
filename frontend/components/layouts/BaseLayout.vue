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
					class="menu-btn"
					@click="drawerLeft = !drawerLeft"
				/>
				<router-link to="/personal/home" class="layout-brand row items-center q-mr-xl">
					<q-icon name="school" size="28px" color="primary" class="brand-icon" />
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
					v-for="(nav, idx) in navigationButtons"
					:key="nav.url"
					:to="nav.url"
					class="nav-link"
					active-class="nav-link-active"
					:style="{ '--stagger': idx }"
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
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
	transition: box-shadow 0.3s var(--anim-ease-out);
}
.header:hover {
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.toolbar {
	min-height: 56px;
	padding: 0 16px;
}

.menu-btn {
	transition: transform 0.25s var(--anim-ease-spring), background 0.2s ease;
}
.menu-btn:hover {
	transform: scale(1.05);
}
.menu-btn:active {
	transform: scale(0.98);
}

.layout-brand {
	text-decoration: none;
	color: inherit;
	transition: opacity 0.2s ease;
	border-radius: 8px;
	padding: 4px 8px;
	margin: -4px -8px;
}
.layout-brand:hover {
	opacity: 0.9;
}
.layout-brand:active {
	opacity: 0.95;
}

.brand-icon {
	transition: transform 0.35s var(--anim-ease-spring);
}
.layout-brand:hover .brand-icon {
	transform: scale(1.08) rotate(-3deg);
}

.brand-text {
	font-weight: 600;
	font-size: 1.1rem;
	color: #1a1a2e;
	letter-spacing: -0.01em;
}

.drawer {
	background: white;
}
.drawer :deep(.q-drawer__content) {
	transition: opacity 0.2s ease;
}

.drawer-content {
	padding-top: 12px;
	padding-bottom: 16px;
}

.nav-link {
	text-decoration: none;
	color: inherit;
	display: block;
	margin: 4px 12px;
	border-radius: 12px;
	transition: background 0.2s ease, transform 0.2s ease;
	animation: fadeInUp 0.35s var(--anim-ease-out) backwards;
	animation-delay: calc(0.04s * (var(--stagger, 0) + 1));
}
.nav-link:hover {
	background: rgba(80, 100, 247, 0.06);
}
.nav-link:active {
	transform: scale(0.99);
}

.nav-link-active .q-item {
	background: rgba(80, 100, 247, 0.12);
	color: #5064f7;
	border-radius: 12px;
	transition: background 0.2s ease, box-shadow 0.2s ease;
	box-shadow: 0 0 0 1px rgba(80, 100, 247, 0.15);
}
.nav-link-active .q-item-label {
	font-weight: 600;
}

.page-container {
	background: #f5f6fa;
}
</style>

