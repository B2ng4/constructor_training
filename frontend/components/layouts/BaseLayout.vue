<template>
	<q-layout view="lHh lpR fFf" class="base-layout">
		<q-header class="header text-grey-9" bordered>
			<q-toolbar class="toolbar">
				<div class="toolbar-inner row items-center no-wrap">
					<q-btn
						v-if="$q.screen.lt.md"
						flat
						dense
						round
						icon="menu"
						class="header-menu-btn"
						@click="drawerLeft = !drawerLeft"
					/>
					<router-link
						to="/personal/home"
						class="layout-brand row items-center no-wrap"
						:class="{ 'layout-brand--icon-only': !$q.screen.gt.xs }"
						:title="!$q.screen.gt.xs ? 'Конструктор тренингов' : undefined"
					>
						<div class="brand-mark flex flex-center">
							<q-icon name="school" size="22px" color="primary" />
						</div>
						<div v-if="$q.screen.gt.xs" class="brand-copy column justify-center q-ml-sm">
							<span class="brand-title">{{ brandTitle }}</span>
							<span v-if="$q.screen.gt.sm && !isEmployee" class="brand-tagline">Личный кабинет</span>
							<span v-else-if="$q.screen.gt.sm && isEmployee" class="brand-tagline">Обучение</span>
						</div>
					</router-link>
					<q-space />
					<BackgroundProcessingIndicator v-if="!isEmployee" />
					<div
						v-if="$q.screen.gt.sm"
						class="header-divider"
						aria-hidden="true"
					/>
					<UserCard />
				</div>
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
			<q-list v-if="navigationButtons.length" class="drawer-nav-list" padding>
				<q-item-label header class="drawer-nav-header">
					Разделы
				</q-item-label>
				<q-item
					v-for="(nav, idx) in navigationButtons"
					:key="nav.url"
					:to="nav.url"
					exact
					clickable
					v-ripple
					class="drawer-nav-item"
					active-class="drawer-nav-item--active"
					:style="{ '--stagger': idx }"
				>
					<q-item-section avatar>
						<q-icon :name="nav.icon" color="grey-7" class="drawer-nav-icon" />
					</q-item-section>
					<q-item-section>
						<q-item-label>{{ nav.name }}</q-item-label>
					</q-item-section>
				</q-item>
			</q-list>
		</q-drawer>

		<q-page-container class="page-container">
			<div class="page-content-slot">
				<router-view v-slot="{ Component, route }">
					<transition name="content-in" mode="out-in" appear>
						<div :key="route.path" class="page-content-view">
							<component :is="Component" />
						</div>
					</transition>
				</router-view>
			</div>
		</q-page-container>
	</q-layout>
</template>

<script>
import { computed, ref } from "vue";
import { storeToRefs } from "pinia";
import UserCard from "@components/features/personal_page/header/UserCard.vue";
import BackgroundProcessingIndicator from "@components/features/personal_page/header/BackgroundProcessingIndicator.vue";
import { useUserStore } from "@store/userData.js";

const CREATOR_NAV = [
	{ name: "Главная", icon: "home", url: "/personal/home" },
	{ name: "Библиотека", icon: "menu_book", url: "/personal/library" },
	{ name: "Мои тренинги", icon: "list_alt", url: "/personal/training" },
	{ name: "Мои курсы", icon: "school", url: "/personal/courses" },
	{ name: "Мои организации", icon: "business", url: "/personal/organizations" },
	{ name: "Поддержка", icon: "help", url: "/personal/help" },
];

export default {
	name: "BaseLayout",
	components: { UserCard, BackgroundProcessingIndicator },
	async mounted() {
		const token = localStorage.getItem("tokenAuth");
		if (token && !useUserStore().isLoaded) {
			await useUserStore().fetchUser();
		}
	},
	setup() {
		const drawerLeft = ref(false);
		const userStore = useUserStore();
		const { isEmployee } = storeToRefs(userStore);

		const navigationButtons = computed(() =>
			isEmployee.value
				? [{ name: "Мои тренинги", icon: "school", url: "/personal/home" }]
				: CREATOR_NAV,
		);

		const brandTitle = computed(() =>
			isEmployee.value ? "SkillSnap" : "SkillSnap - конструктор тренингов",
		);

		return {
			drawerLeft,
			isEmployee,
			navigationButtons,
			brandTitle,
		};
	},
};
</script>

<style scoped>
/*
 * Фон личного кабинета: современный мягкий градиент
 */
.base-layout {
	background-color: #eef2f6;
	background-image:
		radial-gradient(circle at 15% 50%, rgba(80, 100, 247, 0.12) 0, transparent 50%),
		radial-gradient(circle at 85% 30%, rgba(168, 85, 247, 0.08) 0, transparent 50%),
		radial-gradient(circle at 50% 100%, rgba(80, 100, 247, 0.1) 0, transparent 50%);
	background-attachment: fixed;
	height: 100vh;
	min-height: 100vh;
	overflow: hidden;
	position: relative;
}

.base-layout::before {
	content: "";
	position: fixed;
	inset: -5vh -5vw;
	background-image: radial-gradient(rgba(15, 23, 42, 0.05) 1px, transparent 1px);
	background-size: 24px 24px;
	transform: translate3d(0, 0, 0) scale(1.05);
	will-change: transform;
	pointer-events: none;
	z-index: 0;
}

.base-layout::after {
	content: "";
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	height: 400px;
	background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0) 100%);
	pointer-events: none;
	z-index: 0;
}

/* Шапка чуть светлее и с лёгким размытием */
.header {
	background: rgba(255, 255, 255, 0.85) !important;
	backdrop-filter: blur(24px);
	-webkit-backdrop-filter: blur(24px);
	border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
	box-shadow: 0 4px 20px rgba(15, 23, 42, 0.02);
}

.toolbar {
	min-height: 60px;
	padding: 8px 16px;
}

@media (min-width: 1024px) {
	.toolbar {
		padding-left: 24px;
		padding-right: 24px;
	}
}

/* Без max-width и auto-margin: бренд остается у левого края рабочей области (рядом с drawer) */
.toolbar-inner {
	flex: 1 1 auto;
	min-width: 0;
	width: 100%;
	align-items: center;
}

.header-menu-btn {
	color: #475569;
	transition: background 0.2s ease, color 0.2s ease;
	margin-right: 4px;
}

.header-menu-btn:hover {
	background: rgba(0, 0, 0, 0.05);
	color: #1a1a2e;
}

.layout-brand {
	text-decoration: none;
	color: inherit;
	border-radius: 12px;
	padding: 6px 10px 6px 4px;
	margin: 0 8px 0 0;
	transition: background 0.2s ease;
	outline: none;
}

.layout-brand:focus-visible {
	box-shadow: 0 0 0 2px rgba(80, 100, 247, 0.35);
}

.layout-brand--icon-only {
	padding: 4px;
	margin-left: 0;
}

.layout-brand:hover {
	background: rgba(0, 0, 0, 0.03);
}

.layout-brand:active {
	background: rgba(0, 0, 0, 0.045);
}

.brand-mark {
	width: 40px;
	height: 40px;
	border-radius: 11px;
	background: rgba(80, 100, 247, 0.1);
	flex-shrink: 0;
	transition: background 0.2s ease, transform 0.25s var(--anim-ease-spring, ease-out);
}

.layout-brand:hover .brand-mark {
	background: rgba(80, 100, 247, 0.14);
	transform: scale(1.02);
}

.brand-copy {
	min-width: 0;
	line-height: 1.25;
}

.brand-title {
	font-size: 15px;
	font-weight: 700;
	color: #1a1a2e;
	letter-spacing: -0.02em;
}

.brand-tagline {
	font-size: 11px;
	font-weight: 500;
	color: #94a3b8;
	letter-spacing: 0.01em;
	margin-top: 1px;
}

.header-divider {
	width: 1px;
	height: 28px;
	background: rgba(0, 0, 0, 0.08);
	margin-right: 12px;
	margin-left: 4px;
	flex-shrink: 0;
}

.drawer {
	background: rgba(255, 255, 255, 0.85) !important;
	backdrop-filter: blur(24px);
	-webkit-backdrop-filter: blur(24px);
	border-right: 1px solid rgba(0, 0, 0, 0.06) !important;
	position: fixed;
	will-change: transform;
}

:deep(.q-drawer) {
	background: rgba(255, 255, 255, 0.85) !important;
	backdrop-filter: blur(24px);
	-webkit-backdrop-filter: blur(24px);
}

:deep(.q-drawer__content) {
	background: transparent !important;
}

.drawer-nav-header {
	font-size: 11px;
	font-weight: 600;
	letter-spacing: 0.06em;
	text-transform: uppercase;
	color: #64748b;
	padding: 16px 16px 8px;
	line-height: 1.2;
}

.drawer-nav-list {
	padding-top: 4px;
	padding-bottom: 12px;
}

.drawer-nav-item {
	margin: 4px 12px;
	border-radius: 10px;
	transition: all 0.25s ease;
	animation: fadeInUp 0.35s var(--anim-ease-out) backwards;
	animation-delay: calc(0.04s * (var(--stagger, 0) + 1));
	background: transparent;
	border: 1px solid transparent;
	color: #64748b;
}

.drawer-nav-item:hover {
	background: rgba(80, 100, 247, 0.04);
	color: #0f172a;
}

.drawer-nav-item:active {
	transform: scale(0.98);
}

.drawer-nav-item--active {
	background: #ffffff !important;
	color: #5064f7;
	border-color: rgba(0, 0, 0, 0.04);
	box-shadow: 0 4px 12px rgba(80, 100, 247, 0.06);
}

.drawer-nav-item--active :deep(.drawer-nav-icon) {
	color: var(--q-primary) !important;
}

.drawer-nav-item--active :deep(.q-item__label) {
	font-weight: 600;
	color: #5064f7;
}

.page-container {
	background: transparent;
	background-attachment: fixed;
	position: relative;
	z-index: 1;
	height: 100vh;
	overflow-x: hidden;
	overflow-y: auto;
	overscroll-behavior-y: contain;
	scroll-behavior: smooth;
	scrollbar-gutter: stable;
}

.page-content-slot {
	position: relative;
	width: 100%;
	min-height: 100%;
}

.page-content-view {
	width: 100%;
	min-height: calc(100vh - 60px);
}

.page-container::-webkit-scrollbar {
	width: 10px;
}

.page-container::-webkit-scrollbar-track {
	background: transparent;
}

.page-container::-webkit-scrollbar-thumb {
	background: rgba(100, 116, 139, 0.24);
	border: 3px solid transparent;
	border-radius: 999px;
	background-clip: padding-box;
}

.page-container::-webkit-scrollbar-thumb:hover {
	background: rgba(80, 100, 247, 0.42);
	border: 3px solid transparent;
	background-clip: padding-box;
}

/* Плавное появление контента при смене раздела */
.content-in-enter-active {
	position: relative;
	z-index: 1;
	transition: opacity 0.38s var(--anim-ease-out, ease-out),
		transform 0.38s var(--anim-ease-out, ease-out);
	will-change: opacity, transform;
}

.content-in-enter-from {
	opacity: 0;
	transform: translateY(8px);
}

.content-in-leave-active {
	transition: opacity 0.18s var(--anim-ease-in-out, ease-in-out);
}

.content-in-leave-to {
	opacity: 0;
}

/* Внутри раздела — одна общая анимация, без каскада stagger */
.page-container :deep(.animate-fade-in-up),
.page-container :deep(.animate-scale-in) {
	animation: none;
	opacity: 1;
}

.page-container :deep(.animate-stagger-children > *) {
	animation: none;
	opacity: 1;
}

:global(body.body--dark) .base-layout {
	background-color: #080d18;
	background-image:
		radial-gradient(circle at 15% 45%, rgba(80, 100, 247, 0.16) 0, transparent 48%),
		radial-gradient(circle at 85% 25%, rgba(168, 85, 247, 0.10) 0, transparent 45%),
		radial-gradient(circle at 50% 100%, rgba(37, 99, 235, 0.10) 0, transparent 48%);
}

:global(body.body--dark) .base-layout::before {
	background-image: radial-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px);
}

:global(body.body--dark) .base-layout::after {
	background: linear-gradient(180deg, rgba(8, 13, 24, 0.96) 0%, rgba(8, 13, 24, 0) 100%);
}

:global(body.body--dark) .header,
:global(body.body--dark) .drawer,
:global(body.body--dark) :deep(.q-drawer) {
	background: rgba(10, 16, 29, 0.88) !important;
	border-color: rgba(148, 163, 184, 0.13) !important;
	box-shadow: 0 4px 24px rgba(0, 0, 0, 0.18);
}

:global(body.body--dark) .header-menu-btn,
:global(body.body--dark) .drawer-nav-header,
:global(body.body--dark) .drawer-nav-item {
	color: #94a3b8;
}

:global(body.body--dark) .brand-title,
:global(body.body--dark) .drawer-nav-item:hover {
	color: #f1f5f9;
}

:global(body.body--dark) .layout-brand:hover,
:global(body.body--dark) .header-menu-btn:hover,
:global(body.body--dark) .drawer-nav-item:hover {
	background: rgba(148, 163, 184, 0.08);
}

:global(body.body--dark) .header-divider {
	background: rgba(148, 163, 184, 0.16);
}

:global(body.body--dark) .drawer-nav-item--active {
	background: rgba(80, 100, 247, 0.14) !important;
	border-color: rgba(99, 102, 241, 0.2);
	box-shadow: inset 0 0 0 1px rgba(99, 102, 241, 0.05);
}

@media (max-width: 767px) {
	.base-layout {
		height: auto;
		min-height: 100vh;
		overflow: visible;
	}

	.page-container {
		height: auto;
		min-height: 100vh;
		overflow: visible;
		scrollbar-gutter: auto;
	}
}

@media (prefers-reduced-motion: reduce) {
	.header {
		backdrop-filter: none;
		-webkit-backdrop-filter: none;
		background: #eef0f6 !important;
	}

	.content-in-enter-active,
	.content-in-leave-active {
		transition: none !important;
	}

	.content-in-enter-from,
	.content-in-leave-to {
		opacity: 1;
		transform: none;
	}
}
</style>
